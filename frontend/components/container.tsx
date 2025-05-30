"use client";

import React, { useEffect, useState } from "react";
import Navbar from "./navbar";
// Removed direct DOM manipulation and moved logic into React component

type Course = {
  title: string;
  // add other fields as needed
};

async function fetchCourses(): Promise<Course[]> {
  try {
    const response = await fetch("http://localhost:3000/home");
    return await response.json();
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
}

const Container = () => {
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    fetchCourses().then(setCourses);
  }, []);

  return (
    <div>
      <Navbar />
      <main>
        <h1>Available Courses</h1>
        {/* Courses will be dynamically inserted here */}
        <div id="courses">
          {courses.map((course, idx) => (
            <div key={idx}>{course.title}</div>
          ))}
        </div>
        {/* Home button could be used for navigation */}
        <button id="home" onClick={() => fetchCourses().then(setCourses)}>
          Home
        </button>
      </main>
    </div>
  );
};

export default Container;
