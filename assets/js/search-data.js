// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-projects",
          title: "Projects",
          description: "Selected work",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "Below is my CV with an outline of my experiences.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "post-depth-buffer",
        
          title: "Depth Buffer",
        
        description: "Discussion about the inclusion of a depth buffer in my 3D rendering program.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/depth-buffer/";
          
        },
      },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-a-simple-inline-announcement",
          title: 'A simple inline announcement.',
          description: "",
          section: "News",},{id: "news-a-long-announcement-with-details",
          title: 'A long announcement with details',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/announcement_2/";
            },},{id: "news-a-simple-inline-announcement-with-markdown-emoji-sparkles-smile",
          title: 'A simple inline announcement with Markdown emoji! :sparkles: :smile:',
          description: "",
          section: "News",},{id: "projects-built-it",
          title: 'Built-It',
          description: "A location-based AR game where players collect virtual items around the real world.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/built_it/";
            },},{id: "projects-pac-man-ai-agent",
          title: 'Pac-Man AI Agent',
          description: "A Q-learning agent trained to play Pac-Man, evaluated over 1,000 games.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/pacman_ai_agent/";
            },},{id: "projects-patient-portal",
          title: 'Patient Portal',
          description: "A team-built portal letting pharmacists view patient medications and prescribing physicians.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/patient_portal/";
            },},{id: "projects-social-media-platform",
          title: 'Social Media Platform',
          description: "A full-stack social media app with RESTful APIs and MongoDB schemas powering its core features.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/social_media_platform/";
            },},{id: "projects-space-flight",
          title: 'Space Flight',
          description: "A real-time object tracking pipeline comparing centroid tracking and optical flow.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/space_flight/";
            },},{id: "teachings-data-science-fundamentals",
          title: 'Data Science Fundamentals',
          description: "This course covers the foundational aspects of data science, including data collection, cleaning, analysis, and visualization. Students will learn practical skills for working with real-world datasets.",
          section: "Teachings",handler: () => {
              window.location.href = "/teachings/data-science-fundamentals/";
            },},{id: "teachings-introduction-to-machine-learning",
          title: 'Introduction to Machine Learning',
          description: "This course provides an introduction to machine learning concepts, algorithms, and applications. Students will learn about supervised and unsupervised learning, model evaluation, and practical implementations.",
          section: "Teachings",handler: () => {
              window.location.href = "/teachings/introduction-to-machine-learning/";
            },},{
        id: 'social-cv',
        title: 'CV',
        section: 'Socials',
        handler: () => {
          window.open("/assets/pdf/cv.pdf", "_blank");
        },
      },{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%6E%6E%69%63%68%6F%6C%61%73%32%30%32%30@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/natashanicholas2020", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/natasha-nicholas-2245621a8", "_blank");
        },
      },];
