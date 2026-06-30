/**
 * Performance / accessibility helpers — let heavy GSAP / 3D effects stay on
 * desktop while gracefully degrading on mobile and for reduced-motion users.
 * NOTHING here removes an effect; it only decides when to run the full version.
 */
"use client";

import { useEffect, useState } from "react";

/** True when the user prefers reduced motion (OS-level setting). */
export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/**
 * Coarse "is this a low-power / small device" check. Use to pick a LIGHTER
 * animation variant on mobile — not to disable animation entirely.
 */
export function useLowPowerDevice(): boolean {
  const [low, setLow] = useState(false);
  useEffect(() => {
    const smallScreen = window.matchMedia("(max-width: 768px)").matches;
    const fewCores =
      typeof navigator !== "undefined" &&
      typeof navigator.hardwareConcurrency === "number" &&
      navigator.hardwareConcurrency <= 4;
    setLow(smallScreen || fewCores);
  }, []);
  return low;
}

/**
 * Returns the animation tier a component should render:
 *  - "full"    → desktop, full cinematic GSAP / 3D / particles
 *  - "lite"    → mobile / low-power → lighter variant (still premium)
 *  - "static"  → prefers-reduced-motion → no motion, keep final visual state
 */
export function useAnimationTier(): "full" | "lite" | "static" {
  const reduced = usePrefersReducedMotion();
  const low = useLowPowerDevice();
  if (reduced) return "static";
  if (low) return "lite";
  return "full";
}
