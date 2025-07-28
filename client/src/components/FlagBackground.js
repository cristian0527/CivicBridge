import React from "react";
import stars from "../assets/stars.svg"; 

const FlagBackground = () => (
  <div className="absolute inset-0 z-0 pointer-events-none">
    <div
      className="absolute inset-0 bg-repeat opacity-10"
      style={{ backgroundImage: `url(${stars})` }}
    />
    <svg
      viewBox="0 0 1440 320"
      className="absolute top-0 left-0 w-full h-64 animate-[wave_10s_ease-in-out_infinite]"
      preserveAspectRatio="none"
    >
      <path
        fill="#1e3a8a"
        d="M0,64L30,74.7C60,85,120,107,180,128C240,149,300,171,360,176C420,181,480,171,540,170.7C600,171,660,181,720,192C780,203,840,213,900,197.3C960,181,1020,139,1080,112C1140,85,1200,75,1260,80C1320,85,1380,107,1410,117.3L1440,128L1440,0L1410,0C1380,0,1320,0,1260,0C1200,0,1140,0,1080,0C1020,0,960,0,900,0C840,0,780,0,720,0C660,0,600,0,540,0C480,0,420,0,360,0C300,0,240,0,180,0C120,0,60,0,30,0L0,0Z"
      />
    </svg>
  </div>
);

export default FlagBackground;
