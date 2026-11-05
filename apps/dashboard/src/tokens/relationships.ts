export const RELATIONSHIP_TOKENS = {
  types: {
    follower: {
      label: "Follower",
      direction: "inbound",
      badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      icon: "ArrowDownLeft",
    },
    following: {
      label: "Following",
      direction: "outbound",
      badgeColor: "bg-purple-500/10 text-purple-400 border-purple-500/20",
      icon: "ArrowUpRight",
    },
    mutual: {
      label: "Mutual",
      direction: "bidirectional",
      badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      icon: "ArrowLeftRight",
    },
  },
} as const;
