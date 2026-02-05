import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import InputField from "../../components/InputField.jsx";

export default function PublishPanel({
  publishId,
  onPublishIdChange,
  onSubmit,
  isAuthed
}) {
  return (
    <Card>
      <SectionHeader
        title="Publish a generation"
        subtitle="Use a generation id to publish the video."
      />
      <form className="form" onSubmit={onSubmit}>
        <InputField
          label="Generation ID"
          type="number"
          value={publishId}
          onChange={(event) => onPublishIdChange(event.target.value)}
          placeholder="e.g. 12"
          disabled={!isAuthed}
          required
        />
        <Button type="submit" disabled={!isAuthed}>Publish video</Button>
      </form>
    </Card>
  );
}
