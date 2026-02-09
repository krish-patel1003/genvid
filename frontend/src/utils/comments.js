export const countAllComments = (comments = []) =>
  comments.reduce(
    (total, comment) => total + 1 + countAllComments(comment.replies || []),
    0
  );

export const addNestedComment = (comments, targetId, newComment) => {
  if (!targetId) {
    return [{ ...newComment, replies: [] }, ...comments];
  }

  return comments.map((comment) => {
    if (comment.id === targetId) {
      return {
        ...comment,
        replies: [{ ...newComment, replies: [] }, ...(comment.replies || [])]
      };
    }

    if (comment.replies && comment.replies.length) {
      return {
        ...comment,
        replies: addNestedComment(comment.replies, targetId, newComment)
      };
    }

    return comment;
  });
};

export const buildCommentTree = (flatComments = []) => {
  const map = new Map();
  const roots = [];

  flatComments.forEach((comment) => {
    map.set(comment.id, { ...comment, replies: [] });
  });

  flatComments.forEach((comment) => {
    const node = map.get(comment.id);
    if (comment.parentId && map.has(comment.parentId)) {
      map.get(comment.parentId).replies.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
};
