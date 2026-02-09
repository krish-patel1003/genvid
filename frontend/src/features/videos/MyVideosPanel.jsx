import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";

export default function MyVideosPanel({
  videos,
  isAuthed,
  onRefresh,
  onDelete
}) {
  return (
    <Card>
      <SectionHeader
        title="My videos"
        subtitle="View and manage your published content."
        actions={(
          <Button variant="ghost" type="button" onClick={onRefresh} disabled={!isAuthed}>
            Refresh
          </Button>
        )}
      />
      <div className="list">
        {videos.length === 0 && <p className="muted">No videos yet.</p>}
        {videos.map((video) => (
          <div key={video.id} className="list-item">
            <div>
              <strong>Video #{video.id}</strong>
              <p>{video.caption || "Untitled"}</p>
              <p className="muted">Status: {video.status || ""}</p>
            </div>
            <Button variant="danger" type="button" onClick={() => onDelete(video.id)}>
              Delete
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
