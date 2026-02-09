import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import InputField from "../../components/InputField.jsx";

export default function FollowPanel({
  followUserId,
  onFollowUserIdChange,
  isAuthed,
  onFollow,
  onUnfollow,
  onLoadFollowers,
  onLoadFollowing,
  followers,
  following
}) {
  return (
    <Card>
      <SectionHeader
        title="Follow users"
        subtitle="Track creators by user id."
      />
      <div className="form">
        <InputField
          label="User ID"
          type="number"
          value={followUserId}
          onChange={(event) => onFollowUserIdChange(event.target.value)}
          placeholder="e.g. 3"
          disabled={!isAuthed}
        />
        <div className="button-row">
          <Button type="button" onClick={onFollow} disabled={!isAuthed}>
            Follow
          </Button>
          <Button variant="outline" type="button" onClick={onUnfollow} disabled={!isAuthed}>
            Unfollow
          </Button>
        </div>
        <div className="button-row">
          <Button variant="ghost" type="button" onClick={onLoadFollowers}>
            Get followers
          </Button>
          <Button variant="ghost" type="button" onClick={onLoadFollowing}>
            Get following
          </Button>
        </div>
      </div>
      {(followers.length > 0 || following.length > 0) && (
        <div className="grid-two">
          <div>
            <h3>Followers</h3>
            <ul className="plain-list">
              {followers.map((follower) => (
                <li key={follower.id}>{follower.username} ({follower.email})</li>
              ))}
            </ul>
          </div>
          <div>
            <h3>Following</h3>
            <ul className="plain-list">
              {following.map((follow) => (
                <li key={follow.id}>{follow.username} ({follow.email})</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </Card>
  );
}
