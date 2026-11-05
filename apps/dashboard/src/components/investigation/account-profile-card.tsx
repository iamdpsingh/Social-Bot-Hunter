import React from "react";
import { CheckCircle, Calendar, Hash, Users, UserPlus, Image } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { PlatformIcon } from "../ui/platform-icon";
import type { ProfileObservation } from "../../lib/api/types";
import type { Platform } from "../../lib/api/types";

export interface AccountProfileCardProps {
  observation?: ProfileObservation | null;
  platform?: Platform | string;
  accountId?: string;
  username?: string;
  riskScore?: number;
  confidence?: number;
  followers?: number;
  following?: number;
  postsCount?: number;
}

export function AccountProfileCard({
  observation,
  platform = "x",
  accountId = "unknown",
  username: propUsername,
  followers: propFollowers,
  following: propFollowing,
  postsCount: propPostsCount,
}: AccountProfileCardProps) {
  const username = propUsername || observation?.username || accountId || "unknown";
  const followers = propFollowers ?? observation?.followers_count ?? 0;
  const following = propFollowing ?? observation?.following_count ?? 0;
  const posts = propPostsCount ?? observation?.posts_count ?? 0;

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardContent className="p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-slate-800 border border-white/10 text-slate-300 font-bold text-lg">
              {(username || "AC").slice(0, 2).toUpperCase()}
              {observation?.has_default_avatar && (
                <span className="absolute -bottom-1 -right-1 rounded-full bg-amber-500/20 border border-amber-500/40 p-0.5 text-amber-400" title="Default Avatar">
                  <Image className="h-3 w-3" />
                </span>
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-foreground">
                  {observation?.display_name || username}
                </h2>
                {observation?.is_verified && (
                  <span title="Verified Account">
                    <CheckCircle className="h-4 w-4 text-primary fill-primary/20" />
                  </span>
                )}
                <PlatformIcon platform={platform} size={14} />
              </div>
              <p className="text-xs font-mono text-muted-foreground">@{username}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Users className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{followers.toLocaleString()}</span> Followers
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <UserPlus className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{following.toLocaleString()}</span> Following
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Hash className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{posts.toLocaleString()}</span> Posts
            </div>
            {observation?.account_created_at && (
              <div className="flex items-center gap-1.5 text-muted-foreground hidden md:flex">
                <Calendar className="h-3.5 w-3.5" />
                <span>Joined {new Date(observation.account_created_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        {observation?.bio && (
          <p className="mt-4 text-xs text-slate-300 bg-white/5 p-3 rounded-lg border border-white/5">
            {observation.bio}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
