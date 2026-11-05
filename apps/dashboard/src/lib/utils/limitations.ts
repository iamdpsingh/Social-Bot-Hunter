export function formatLimitationNotice(limitationKey: string): { title: string; explanation: string } {
  const notices: Record<string, { title: string; explanation: string }> = {
    unobservable_posts: {
      title: "Private Post Visibility",
      explanation: "Recent content and media interactions are private and excluded from scoring.",
    },
    rate_limit_truncation: {
      title: "Rate Limit Quota Truncation",
      explanation: "Collection capped at allowable platform rate limits; coverage is partial.",
    },
    missing_account_creation_date: {
      title: "Creation Timestamp Unavailable",
      explanation: "Platform API does not expose exact registration timestamp.",
    },
  };

  return notices[limitationKey] || {
    title: "Collection Limitation",
    explanation: limitationKey,
  };
}
