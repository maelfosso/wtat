mod models;

use reqwest::blocking::Client;
use reqwest::Error;
use tracing::{debug, error};

use models::{GetPostsResponse};

pub fn get_posts_from_fb_pages(client: &Client, host: &String, page_id: &String, cursor: Option<String>) -> Result<GetPostsResponse, Error> {
    let mut url = format!(
        "https://{}/page/posts?page_id={}",
        host,
        page_id
    );
    if let Some(c) = cursor {
        url.push_str(&format!("&cursor={}", c));
    }
    
    // Truncate URL for logging (privacy)
    let truncated_url = if url.len() > 100 {
        format!("{}...", &url[..100])
    } else {
        url.clone()
    };
    debug!(url = %truncated_url, "Fetching posts");

    let response = client.get(url).send()?;
    let text = response.text()?;
    // Removed the full JSON dump for privacy
    
    let body = serde_json::from_str(&text).map_err(|e| {
        error!("Parsing error: {}", e);
        panic!("STOP DEBUGGING");
    });
    // Ok(body)
    body
}