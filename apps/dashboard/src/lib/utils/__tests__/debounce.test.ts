import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { debounce } from "../debounce";

describe("debounce utility", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("delays function execution until delay elapsed", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 150);

    debounced("a");
    debounced("b");
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(150);
    expect(fn).toHaveBeenCalledTimes(1);
    expect(fn).toHaveBeenCalledWith("b");
  });

  it("cancels pending invocation when cancel is called", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 150);

    debounced("test");
    debounced.cancel();
    vi.advanceTimersByTime(150);
    expect(fn).not.toHaveBeenCalled();
  });
});
