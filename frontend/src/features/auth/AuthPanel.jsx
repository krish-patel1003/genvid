import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import InputField from "../../components/InputField.jsx";
import TextAreaField from "../../components/TextAreaField.jsx";

export default function AuthPanel({
  isAuthed,
  authMode,
  onModeChange,
  authForm,
  onAuthChange,
  onAuthSubmit,
  profileForm,
  onProfileChange,
  onProfileSubmit,
  googleUrl
}) {
  return (
    <Card>
      <SectionHeader
        title={isAuthed ? "Account" : "Get started"}
        subtitle={isAuthed ? "Manage your profile and identity." : "Create an account or log in to continue."}
      />

      {!isAuthed ? (
        <form className="form" onSubmit={onAuthSubmit}>
          <div className="segmented">
            <button
              type="button"
              className={authMode === "login" ? "active" : ""}
              onClick={() => onModeChange("login")}
            >
              Sign in
            </button>
            <button
              type="button"
              className={authMode === "signup" ? "active" : ""}
              onClick={() => onModeChange("signup")}
            >
              Sign up
            </button>
          </div>

          {authMode === "signup" && (
            <InputField
              label="Email"
              type="email"
              value={authForm.email}
              onChange={(event) => onAuthChange({ email: event.target.value })}
              placeholder="you@example.com"
              required
            />
          )}

          <InputField
            label="Username"
            type="text"
            value={authForm.username}
            onChange={(event) => onAuthChange({ username: event.target.value })}
            placeholder="yourhandle"
            required
          />

          <InputField
            label="Password"
            type="password"
            value={authForm.password}
            onChange={(event) => onAuthChange({ password: event.target.value })}
            placeholder="Minimum 8 characters"
            required
          />

          <Button type="submit">
            {authMode === "signup" ? "Create account" : "Sign in"}
          </Button>
          <a className="btn outline" href={googleUrl}>Sign in with Google</a>
        </form>
      ) : (
        <form className="form" onSubmit={onProfileSubmit}>
          <InputField
            label="Username"
            type="text"
            value={profileForm.username}
            onChange={(event) => onProfileChange({ username: event.target.value })}
          />
          <TextAreaField
            label="Bio"
            rows="3"
            value={profileForm.bio}
            onChange={(event) => onProfileChange({ bio: event.target.value })}
            placeholder="Share a short bio"
          />
          <InputField
            label="Profile image URL"
            type="text"
            value={profileForm.profile_pic}
            onChange={(event) => onProfileChange({ profile_pic: event.target.value })}
            placeholder="https://"
          />
          <Button type="submit">Update profile</Button>
        </form>
      )}
    </Card>
  );
}
