import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import InputField from "../../components/InputField.jsx";
import Chip from "../../components/Chip.jsx";

export default function VideoLookupPanel({
  lookupVideoId,
  onLookupIdChange,
  onSubmit,
  video
}) {
  return (
    <Card>
      <SectionHeader
        title="Video lookup"
        subtitle="Fetch a public video by id."
      />
      <form className="form" onSubmit={onSubmit}>
        <InputField
          label="Video ID"
          type="number"
          value={lookupVideoId}
          onChange={(event) => onLookupIdChange(event.target.value)}
          placeholder="e.g. 5"
        />
        <Button type="submit">Fetch video</Button>
      </form>
      {video && (
        <div className="list-item">
          <div>
            <strong>Video #{video.id}</strong>
            <p>{video.caption || "Untitled"}</p>
            <p className="muted">{video.status || ""}</p>
          </div>
          <Chip>Owner #{video.owner_id}</Chip>
        </div>
      )}
    </Card>
  );
}
