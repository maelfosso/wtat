use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Response of the /page/posts endpoint.
#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GetPostsResponse {
    pub results: Vec<Post>,
    pub cursor: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Post {
    // Required: a post without id or date is unusable
    pub post_id: String,
    pub timestamp: u64,

    #[serde(rename = "type")]
    pub post_type: Option<String>,
    pub url: Option<String>,
    pub message: Option<String>,
    pub message_rich: Option<String>,

    // Engagement
    pub comments_count: Option<u32>,
    pub reactions_count: Option<u32>,
    pub reshare_count: Option<u32>,
    pub reactions: Option<Reactions>,
    pub video_view_count: Option<Value>, // only seen as null so far

    // Authorship
    pub author: Option<Author>,
    pub authors: Option<Vec<Author>>,
    pub author_title: Option<String>,

    // Media
    pub image: Option<Image>,
    pub images_count: Option<Value>, // only seen as null so far
    pub album_preview: Option<Value>,
    pub video: Option<String>,
    pub video_files: Option<VideoFiles>,
    pub video_thumbnail: Option<String>,

    // Attachments and links
    pub external_url: Option<String>,
    pub attached_event: Option<Value>,
    pub attached_group: Option<Value>,
    pub attached_post: Option<Value>,
    pub attached_post_url: Option<String>,
    pub associated_group_id: Option<Value>, // only seen as null so far
    pub associated_group: Option<Value>,
    pub text_format_metadata: Option<Value>,

    // Interactions
    pub comments_id: Option<String>,
    pub shares_id: Option<String>,
    pub top_comments: Option<Vec<TopComment>>,

    /// Any field not declared above, kept as-is so nothing is silently dropped.
    #[serde(flatten)]
    pub extra: HashMap<String, Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Reactions {
    pub angry: Option<u32>,
    pub care: Option<u32>,
    pub haha: Option<u32>,
    pub like: Option<u32>,
    pub love: Option<u32>,
    pub sad: Option<u32>,
    pub wow: Option<u32>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Author {
    pub id: Option<String>,
    pub name: Option<String>,
    pub url: Option<String>,
    pub profile_picture_url: Option<String>,
    pub delegate_page_id: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Image {
    pub id: Option<String>,
    pub uri: Option<String>,
    pub url: Option<String>,
    pub height: Option<u32>,
    pub width: Option<u32>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct VideoFiles {
    pub video_hd_file: Option<String>,
    pub video_sd_file: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TopComment {
    #[serde(rename = "type")]
    pub comment_type: Option<String>,
    pub id: Option<String>,
    pub legacy_fb_id: Option<String>,
    pub text: Option<String>,
    pub author: Option<CommentAuthor>,
    pub created_time: Option<u64>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CommentAuthor {
    pub id: Option<String>,
    pub name: Option<String>,
    pub url: Option<String>,
    pub gender: Option<String>,
    pub profile_image_url: Option<String>,
}

/// Why the collection loop stopped.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StopReason {
    EndOfPagination,
    RetriesExhausted,
    FatalError,
}

impl StopReason {
    pub fn as_str(self) -> &'static str {
        match self {
            StopReason::EndOfPagination => "end_of_pagination",
            StopReason::RetriesExhausted => "retries_exhausted",
            StopReason::FatalError => "fatal_error",
        }
    }
}
