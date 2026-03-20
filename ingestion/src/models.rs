use serde::{Deserialize, Serialize};

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GetPostsResponse {
  pub results: Vec<Post>,
  pub cursor: Option<String>
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Reactions {
  pub angry: u32,
  pub care: u32,
  pub haha: u32,
  pub like: u32,
  pub love: u32,
  pub sad: u32,
  pub wow: u32
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Author {
  pub id: String,
  pub name: String,
  pub url: String,
  pub profile_picture_url: String
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Image {
  pub uri: Option<String>,
  pub url: Option<String>,
  pub height: Option<u32>,
  pub width: Option<u32>,
  pub id: String
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Post {
  pub post_id: String,

  #[serde(rename = "type")]
  pub post_type: String,

  pub url: String,
  pub message: String,
  pub message_rich: String,
  pub timestamp: u64,
  pub comments_count: u32,
  pub reactions_count: u32,
  pub reshare_count: u32,
  pub reactions: Option<Reactions>,
  pub author: Option<Author>,
  pub author_title: Option<String>,
  pub image: Option<Image>,

  pub video: Option<serde_json::Value>,
  pub album_preview: Option<serde_json::Value>,
  pub video_files: Option<serde_json::Value>,
  pub video_thumbnail: Option<serde_json::Value>,
  pub external_url: Option<String>,
  pub attached_event: Option<serde_json::Value>,
  pub attached_post: Option<serde_json::Value>,
  pub attached_post_url: Option<String>,
  pub text_format_metadata: Option<serde_json::Value>,
  
  pub comments_id: String,
  pub shares_id: String
}
