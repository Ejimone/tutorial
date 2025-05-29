fetch("http://localhost:8000/home")
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.error("Error fetching data:", error));
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, setting up event listeners");
  const homeButton = document.getElementById("home");
  const assignmentsButton = document.getElementById("assignments");
  console.log("Home button found:", homeButton);
  console.log("Assignments button found:", assignmentsButton);

  // Home button click event (courses)
  homeButton.addEventListener("click", function (e) {
    console.log("Home/Courses button clicked!");
    e.preventDefault(); // Prevent default link behavior

    fetch("http://localhost:8000/home")
      .then((response) => {
        console.log("Response received:", response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Data received:", data);
        const heroSection = document.getElementById("herosection");
        const ul = heroSection.querySelector("ul");
        console.log("Hero section found:", heroSection);
        console.log("UL element found:", ul);

        // Clear existing content
        ul.innerHTML = "";

        if (data.courses && data.courses.length > 0) {
          console.log(`Displaying ${data.courses.length} courses`);
          data.courses.forEach((course) => {
            console.log("Processing course:", course.name);
            const li = document.createElement("li");
            li.innerHTML = `
              <h3>${course.name}</h3>
              <p>Course ID: ${course.id}</p>
              <p>Description: ${
                course.description || "No description available"
              }</p>
              <p>State: ${course.courseState}</p>
              <hr>
            `;
            ul.appendChild(li);
          });
          console.log("All courses added to DOM");
        } else {
          console.log("No courses found in data");
          ul.innerHTML = "<li><h3>No courses found</h3></li>";
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        const heroSection = document.getElementById("herosection");
        const ul = heroSection.querySelector("ul");
        ul.innerHTML = "<li><h3>Error loading courses</h3></li>";
      });
  });

  // Assignments button click event
  assignmentsButton.addEventListener("click", function (e) {
    console.log("Assignments button clicked!");
    e.preventDefault(); // Prevent default link behavior

    fetch("http://localhost:8000/assignments")
      .then((response) => {
        console.log("Assignments response received:", response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Assignments data received:", data);
        const heroSection = document.getElementById("herosection");
        const ul = heroSection.querySelector("ul");
        console.log("Hero section found:", heroSection);
        console.log("UL element found:", ul);

        // Clear existing content
        ul.innerHTML = "";

        // Check if we have assignments_by_course data
        if (
          data.assignments_by_course &&
          data.assignments_by_course.length > 0
        ) {
          console.log(
            `Processing ${data.assignments_by_course.length} courses for assignments`
          );

          let totalAssignments = 0;
          data.assignments_by_course.forEach((courseData) => {
            const courseName = courseData.courseName || "Unknown Course";
            const assignments = courseData.assignments || [];

            if (assignments.length > 0) {
              // Add a course header
              const courseHeader = document.createElement("li");
              courseHeader.innerHTML = `
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 5px;">
                  📚 ${courseName} (${assignments.length} assignments)
                </h2>
              `;
              ul.appendChild(courseHeader);

              // Add assignments for this course
              assignments.forEach((assignment) => {
                console.log(
                  `Processing assignment: ${assignment.title} from course: ${courseName}`
                );
                totalAssignments++;
                const li = document.createElement("li");
                li.style.marginLeft = "20px"; // Indent assignments under course
                li.innerHTML = `
                  <h3>${assignment.title}</h3>
                  <p><strong>Assignment ID:</strong> ${assignment.id}</p>
                  <p><strong>Course:</strong> ${courseName}</p>
                  <p><strong>Description:</strong> ${
                    assignment.description || "No description available"
                  }</p>
                  <p><strong>Due Date:</strong> ${
                    assignment.dueDate
                      ? new Date(assignment.dueDate).toLocaleDateString()
                      : "No due date"
                  }</p>
                  <p><strong>State:</strong> ${
                    assignment.state || "Unknown"
                  }</p>
                  <p><strong>Work Type:</strong> ${
                    assignment.workType || "Assignment"
                  }</p>
                  <hr style="margin: 15px 0;">
                `;
                ul.appendChild(li);
              });
            } else {
              // Show courses with no assignments
              const courseHeader = document.createElement("li");
              courseHeader.innerHTML = `
                <h3 style="color: #6b7280;">📚 ${courseName}</h3>
                <p style="margin-left: 20px; font-style: italic;">No assignments found</p>
                <hr>
              `;
              ul.appendChild(courseHeader);
            }
          });

          console.log(
            `All assignments added to DOM. Total: ${totalAssignments} assignments`
          );

          // Add summary at the top
          if (totalAssignments > 0) {
            const summary = document.createElement("li");
            summary.innerHTML = `
              <h2 style="background: #f3f4f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                📋 Total: ${totalAssignments} assignments across ${data.assignments_by_course.length} courses
              </h2>
            `;
            ul.insertBefore(summary, ul.firstChild);
          }
        } else {
          console.log("No assignments found in assignments_by_course");
          ul.innerHTML = "<li><h3>No assignments found</h3></li>";
        }
      })
      .catch((error) => {
        console.error("Error fetching assignments:", error);
        const heroSection = document.getElementById("herosection");
        const ul = heroSection.querySelector("ul");
        ul.innerHTML = "<li><h3>Error loading assignments</h3></li>";
      });
  });
});

// body background color should change every 1 second, it should be flowing, also the  colors should be random, it should be changing smoothly, easing and a transition should be applied
document.body.style.transition = "background-color 1s ease-in-out";
setInterval(() => {
  const randomColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
  document.body.style.backgroundColor = randomColor;
}, 1000);
