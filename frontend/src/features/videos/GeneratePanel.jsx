import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import TextAreaField from "../../components/TextAreaField.jsx";
import Chip from "../../components/Chip.jsx";

export default function GeneratePanel({
  prompt,
  onPromptChange,
  onSubmit,
  isAuthed,
  items
}) {
  return (
    <Card>
      <SectionHeader
        title="Generate a video"
        subtitle="Submit a prompt to start a generation job."
      />
      <form className="form" onSubmit={onSubmit}>
        <TextAreaField
          label="Prompt"
          rows="3"
          value={prompt}
          onChange={(event) => onPromptChange(event.target.value)}
          placeholder="Describe the video you want to generate"
          required
          disabled={!isAuthed}
        />
        <Button type="submit" disabled={!isAuthed}>Create generation</Button>
      </form>
      {items.length > 0 && (
        <div className="list">
          {items.map((item) => (
            <div key={`${item.id}-${item.created_at || ""}`} className="list-item">
              <div>
                <strong>Generation #{item.id}</strong>
                <p>Status: {item.status || "pending"}</p>
                <p className="muted">{item.created_at || ""}</p>
              </div>
              <Chip>{item.prompt || ""}</Chip>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
