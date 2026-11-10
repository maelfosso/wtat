use std::fs;
use std::process::ExitCode;
use std::time::{Duration, Instant};

use serde::{Serialize, Deserialize};
use reqwest::header::{HeaderMap, HeaderValue};
use tracing::{info, debug, error, warn, span, Level};

use clap::Parser;

use wtat_ingestion::{get_posts_from_fb_pages, is_retryable};

use wtat_ingestion::models::StopReason;

const REQUEST_TIMEOUT_SECS: u64 = 60;
const MAX_ATTEMPTS: u32 = 3;
const BASE_BACKOFF_SECS: u64 = 5;
const PAGE_DELAY_SECS: u64 = 1;


#[derive(Serialize, Deserialize)]
struct  ScrapeState {
  last_cursor: Option<String>
}

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
  #[arg(short, long)]
  page_id: String,
}

use tracing_appender::non_blocking::WorkerGuard;
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

/// Sets up console and JSON file logging.
/// The returned guard must be kept alive until the end of `main`,
/// otherwise buffered log lines are lost on exit.
fn init_tracing(log_path: &str) -> WorkerGuard {
    fs::create_dir_all(log_path).expect("Failed to create log directory");

    // File writer: daily rotation, written from a background thread
    let file_appender = tracing_appender::rolling::daily(log_path, "ingestion.log");
    let (file_writer, guard) = tracing_appender::non_blocking(file_appender);

    // Level filter: RUST_LOG if set, otherwise "info"
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    // Console: compact, human-readable
    let console_layer = fmt::layer()
        .compact()
        .with_writer(std::io::stderr);

    // File: JSON Lines, including the current span fields (page_id)
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
    
    let data_path = std::env::var("DATA_PATH").expect(
        "DATA_PATH is missing"
    );
    // let page_id = std::env::var("FB_PAGE_ID").expect("FB_PAGE_ID is missing");
    let rapid_api_key: String = std::env::var("RAPID_API_KEY").expect(
        "RAPID_API_KEY not set"
    );
    let rapid_api_host: String = std::env::var("RAPID_API_HOST").expect(
        "RAPID_API_HOST not set"
    );

    let args = Args::parse();
    let page_id = args.page_id;

    let state_path = format!("{}/{}/state.json", data_path, page_id);
    let mut current_cursor = if let Ok(content) = fs::read_to_string(&state_path) {
        let state: ScrapeState = serde_json::from_str(&content).unwrap_or(ScrapeState { last_cursor: None });

        state.last_cursor
    } else {
        None
    };

    let dir_path = format!("{}/{}", data_path, page_id);
    fs::create_dir_all(&dir_path).expect("Impossible to create a directory");

    let mut headers = HeaderMap::new();
    headers.insert("x-rapidapi-key", HeaderValue::from_str(&rapid_api_key).unwrap());
    headers.insert("x-rapidapi-host", HeaderValue::from_str(&rapid_api_host).unwrap());
    headers.insert("Content-Type", HeaderValue::from_static("application/json"));

    let client = reqwest::blocking::Client::builder()
        .default_headers(headers)
        .timeout(Duration::from_secs(REQUEST_TIMEOUT_SECS))
        .build()
        .unwrap()
        ;
    
    let start_time = Instant::now();
    let mut total_posts = 0;
    let mut pages_fetched = 0;
    
    let collect_span = span!(Level::INFO, "collect", page_id = page_id.clone());
    let _enter = collect_span.enter();

    let stop_reason = loop {

        let request_start = Instant::now();
        let mut attempt = 1;

        debug!("Collecting with cursor: {:?}", current_cursor);

        let result = loop {
            match get_posts_from_fb_pages(&client, &rapid_api_host, &page_id, current_cursor.clone()) {
                Ok(response) => break Ok(response),
                Err(err) if is_retryable(&err) && attempt < MAX_ATTEMPTS => {
                    let backoff = Duration::from_secs(BASE_BACKOFF_SECS * 2u64.pow(attempt - 1));
                    warn!(
                        attempt,
                        max_attemps = MAX_ATTEMPTS,
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
            fs::write(filename, json_data)
                .unwrap_or_else(|e| panic!("Error writing file for post {}: {}", post.post_id, e));
            debug!(post_id = %post.post_id, "Post written to file");
        }

        info!(
            page = pages_fetched,
            posts_received = posts.len(),
            attempts = attempt,
            duration_ms = request_start.elapsed().as_millis() as u64,
            "Page fetched"
        );

        if response.cursor.is_none() || response.cursor == current_cursor {
            break StopReason::EndOfPagination;
        }

        current_cursor = response.cursor;
        let state = ScrapeState {
            last_cursor: current_cursor.clone()
        };
        let state_json = serde_json::to_string(&state).unwrap();
        fs::write(&state_path, state_json).expect("Failed to save state");

        std::thread::sleep(std::time::Duration::from_secs(PAGE_DELAY_SECS));
    };

    info!(
        pages_fetched,
        posts_written = total_posts,
        duration_ms = start_time.elapsed().as_millis() as u64,
        stop_reason = stop_reason.as_str(),
        "Collection finished"
    );

    if stop_reason == StopReason::EndOfPagination {
        ExitCode::SUCCESS
    } else {
        ExitCode::FAILURE
    }
}
