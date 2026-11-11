use std::fs;
use std::process::ExitCode;
use std::time::{Duration, Instant};

use chrono::{DateTime, NaiveDate};
use clap::Parser;
use reqwest::header::{HeaderMap, HeaderValue};
use serde::{Deserialize, Serialize};
use tracing::{debug, error, info, span, warn, Level};
use tracing_appender::non_blocking::WorkerGuard;
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

use wtat_ingestion::models::StopReason;
use wtat_ingestion::{get_posts_from_fb_pages, is_retryable};

const REQUEST_TIMEOUT_SECS: u64 = 60;
const MAX_ATTEMPTS: u32 = 3;
const BASE_BACKOFF_SECS: u64 = 5;
const PAGE_DELAY_SECS: u64 = 1;

#[derive(Serialize, Deserialize)]
struct ScrapeState {
    last_cursor: Option<String>,
}

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Facebook page to collect.
    #[arg(short, long)]
    page_id: String,

    /// Name of this collection run. Posts are written to DATA_PATH/<page_id>/<run_id>/.
    /// Reuse the same name to resume an interrupted run.
    #[arg(short, long)]
    run_id: String,

    /// Stop once a whole page of results is older than this date (YYYY-MM-DD).
    /// Without it, the run goes back to the very first post.
    #[arg(long)]
    until: Option<NaiveDate>,
}

/// Sets up console and JSON file logging.
/// The returned guard must be kept alive until the end of `main`.
fn init_tracing(log_path: &str) -> WorkerGuard {
    fs::create_dir_all(log_path).expect("Failed to create log directory");

    let file_appender = tracing_appender::rolling::daily(log_path, "ingestion.log");
    let (file_writer, guard) = tracing_appender::non_blocking(file_appender);

    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("warn,wtat_ingestion=info"));

    let console_layer = fmt::layer().compact().with_writer(std::io::stderr);

    let file_layer = fmt::layer()
        .json()
        .with_current_span(true)
        .with_span_list(false)
        .with_writer(file_writer);

    tracing_subscriber::registry()
        .with(filter)
        .with(console_layer)
        .with(file_layer)
        .init();

    guard
}

fn main() -> ExitCode {
    dotenvy::dotenv().ok();

    let log_path = std::env::var("LOG_PATH").expect("LOG_PATH is missing");
    let _guard = init_tracing(&log_path);

    let data_path = std::env::var("DATA_PATH").expect("DATA_PATH is missing");
    let rapid_api_key = std::env::var("RAPID_API_KEY").expect("RAPID_API_KEY not set");
    let rapid_api_host = std::env::var("RAPID_API_HOST").expect("RAPID_API_HOST not set");

    let args = Args::parse();
    let page_id = args.page_id;
    let run_id = args.run_id;
    let until = args.until;

    // The limit as a Unix timestamp, at midnight UTC of the given date
    let until_ts: Option<i64> =
        until.map(|date| date.and_hms_opt(0, 0, 0).unwrap().and_utc().timestamp());

    // One folder per run: nothing from a previous run is ever overwritten
    let dir_path = format!("{}/{}/{}", data_path, page_id, run_id);
    fs::create_dir_all(&dir_path).expect("Failed to create the run directory");
    let state_path = format!("{}/state.json", dir_path);

    // Resume this run if it was interrupted, otherwise start from the newest post
    let mut current_cursor = fs::read_to_string(&state_path)
        .ok()
        .and_then(|content| serde_json::from_str::<ScrapeState>(&content).ok())
        .and_then(|state| state.last_cursor);

    let mut headers = HeaderMap::new();
    headers.insert("x-rapidapi-key", HeaderValue::from_str(&rapid_api_key).unwrap());
    headers.insert("x-rapidapi-host", HeaderValue::from_str(&rapid_api_host).unwrap());
    headers.insert("Content-Type", HeaderValue::from_static("application/json"));

    let client = reqwest::blocking::Client::builder()
        .default_headers(headers)
        .timeout(Duration::from_secs(REQUEST_TIMEOUT_SECS))
        .build()
        .unwrap();

    let collect_span = span!(Level::INFO, "collect", page_id = %page_id, run_id = %run_id);
    let _enter = collect_span.enter();

    info!(
        until = ?until,
        resumed = current_cursor.is_some(),
        "Collection started"
    );

    let start_time = Instant::now();
    let mut total_posts = 0;
    let mut pages_fetched = 0;

    let stop_reason = loop {
        let request_start = Instant::now();
        let mut attempt = 1;

        // Retry the same cursor on transient errors
        let result = loop {
            match get_posts_from_fb_pages(&client, &rapid_api_host, &page_id, current_cursor.clone()) {
                Ok(response) => break Ok(response),
                Err(err) if is_retryable(&err) && attempt < MAX_ATTEMPTS => {
                    let backoff = Duration::from_secs(BASE_BACKOFF_SECS * 2u64.pow(attempt - 1));
                    warn!(
                        attempt,
                        max_attempts = MAX_ATTEMPTS,
                        backoff_secs = backoff.as_secs(),
                        error = %err.without_url(),
                        "Request failed, retrying"
                    );
                    std::thread::sleep(backoff);
                    attempt += 1;
                }
                Err(err) => break Err(err),
            }
        };

        let response = match result {
            Ok(response) => response,
            Err(err) => {
                let reason = if is_retryable(&err) {
                    StopReason::RetriesExhausted
                } else {
                    StopReason::FatalError
                };
                error!(attempts = attempt, error = %err.without_url(), "Request failed, stopping");
                break reason;
            }
        };

        let posts = response.results;
        pages_fetched += 1;
        total_posts += posts.len();

        for post in &posts {
            let filename = format!("{}/{}.json", dir_path, post.post_id);
            let json_data = serde_json::to_string_pretty(&post)
                .unwrap_or_else(|e| panic!("Serialization error for post {}: {}", post.post_id, e));
            fs::write(&filename, json_data)
                .unwrap_or_else(|e| panic!("Error writing file for post {}: {}", post.post_id, e));
            debug!(post_id = %post.post_id, "Post written to file");
        }

        // Date of the oldest post of this page, to follow the progress back in time
        let oldest_post = posts
            .iter()
            .map(|post| post.timestamp)
            .min()
            .and_then(|ts| DateTime::from_timestamp(ts as i64, 0))
            .map(|date| date.date_naive().to_string())
            .unwrap_or_else(|| "-".to_string());

        info!(
            page = pages_fetched,
            posts_received = posts.len(),
            oldest_post = %oldest_post,
            attempts = attempt,
            duration_ms = request_start.elapsed().as_millis() as u64,
            "Page fetched"
        );

        if response.cursor.is_none() || response.cursor == current_cursor {
            break StopReason::EndOfPagination;
        }

        // Save the cursor before any stop, so the run can be resumed or extended later
        current_cursor = response.cursor;
        let state = ScrapeState { last_cursor: current_cursor.clone() };
        let state_json = serde_json::to_string(&state).unwrap();
        fs::write(&state_path, state_json).expect("Failed to save state");

        // Stop once the whole page is older than the limit
        let past_until = match until_ts {
            Some(limit) => !posts.is_empty() && posts.iter().all(|post| (post.timestamp as i64) < limit),
            None => false,
        };
        if past_until {
            break StopReason::ReachedUntil;
        }

        std::thread::sleep(Duration::from_secs(PAGE_DELAY_SECS));
    };

    info!(
        pages_fetched,
        posts_written = total_posts,
        duration_ms = start_time.elapsed().as_millis() as u64,
        stop_reason = stop_reason.as_str(),
        "Collection finished"
    );

    match stop_reason {
        StopReason::EndOfPagination | StopReason::ReachedUntil => ExitCode::SUCCESS,
        _ => ExitCode::FAILURE,
    }
}
