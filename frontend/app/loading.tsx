"use client";

import { useState, useEffect } from "react";
import styles from "./loading.module.css";

interface LoadingScreenProps {
  onLoadingComplete?: () => void;
  duration?: number;
}

export default function LoadingScreen({ 
  onLoadingComplete, 
  duration = 2500 
}: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);
  const [isHidden, setIsHidden] = useState(false);

  useEffect(() => {
    // Animate progress from 0 to 100
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        // Exponential ease-out for smooth acceleration/deceleration
        return Math.min(prev + (100 - prev) * 0.1, 100);
      });
    }, 30);

    // Hide loading screen after duration
    const timer = setTimeout(() => {
      setIsHidden(true);
      if (onLoadingComplete) {
        setTimeout(() => {
          onLoadingComplete();
        }, 800); // Wait for fade out animation
      }
    }, duration);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [duration, onLoadingComplete]);

  const circumference = 2 * Math.PI * 100; // radius = 100
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className={`${styles.loadingScreen} ${isHidden ? styles.hidden : ''}`}>
      {/* Neon Edge Lights */}
      <div className={styles.neonEdges}>
        <div className={`${styles.neonEdge} ${styles.neonEdgeTop}`}></div>
        <div className={`${styles.neonEdge} ${styles.neonEdgeBottom}`}></div>
        <div className={`${styles.neonEdge} ${styles.neonEdgeLeft}`}></div>
        <div className={`${styles.neonEdge} ${styles.neonEdgeRight}`}></div>
      </div>

      {/* Light Streaks */}
      <div className={styles.lightStreaks}>
        <div className={styles.lightStreak} style={{ '--rotation': '45deg' } as React.CSSProperties}></div>
        <div className={styles.lightStreak} style={{ '--rotation': '-45deg' } as React.CSSProperties}></div>
        <div className={styles.lightStreak} style={{ '--rotation': '135deg' } as React.CSSProperties}></div>
        <div className={styles.lightStreak} style={{ '--rotation': '-135deg' } as React.CSSProperties}></div>
      </div>

      <div className={styles.loadingContainer}>
        {/* Basketball Container with Progress Ring */}
        <div className={styles.basketballContainer}>
          {/* Circular Progress Ring */}
          <div className={styles.progressRing}>
            <svg className={styles.progressRingSVG} viewBox="0 0 220 220">
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#ff8c00" stopOpacity="1" />
                  <stop offset="50%" stopColor="#ff6b35" stopOpacity="1" />
                  <stop offset="100%" stopColor="#ff8c00" stopOpacity="1" />
                </linearGradient>
              </defs>
              <circle
                className={styles.progressRingBackground}
                cx="110"
                cy="110"
                r="100"
              />
              <circle
                className={styles.progressRingForeground}
                cx="110"
                cy="110"
                r="100"
                style={{
                  strokeDashoffset: offset
                }}
              />
            </svg>
          </div>

          {/* Glowing Ring Pulse */}
          <div className={styles.progressGlow}></div>

          {/* Percentage Display */}
          <div className={styles.percentageDisplay}>
            {Math.round(progress)}%
          </div>

          {/* True 3D Basketball Sphere */}
          <div className={styles.basketball3D}>
            <div className={styles.basketballSphere}>
              {/* Outer sphere with lighting */}
              <div className={styles.basketballOuter}></div>
              
              {/* Inner sphere with pattern */}
              <div className={styles.basketballInner}>
                <div className={styles.basketballPattern}>
                  {/* Center vertical line */}
                  <div className={styles.ballLineVertical}></div>
                  {/* Center horizontal line */}
                  <div className={styles.ballLineHorizontal}></div>
                  {/* Curved lines */}
                  <div className={styles.ballCurve1}></div>
                  <div className={styles.ballCurve2}></div>
                  <div className={styles.ballCurve3}></div>
                  <div className={styles.ballCurve4}></div>
                </div>
              </div>
              
              {/* Highlights for 3D effect */}
              <div className={styles.basketballHighlight}></div>
              <div className={styles.basketballShadowOverlay}></div>
            </div>
          </div>

          {/* Basketball Shadow */}
          <div className={styles.basketballShadow}></div>
        </div>

        {/* Dynamic Particles */}
        <div className={styles.particles}>
          <div className={styles.particle}></div>
          <div className={styles.particle}></div>
          <div className={styles.particle}></div>
          <div className={styles.particle}></div>
          <div className={styles.particle}></div>
          <div className={styles.particle}></div>
        </div>

        {/* Loading Text */}
        <div className={styles.loadingText}>
          <h2 className={styles.loadingTitle}>PredictiveEdge</h2>
          <p className={styles.loadingSubtitle}>Loading Analytics Dashboard...</p>
        </div>
      </div>
    </div>
  );
}
