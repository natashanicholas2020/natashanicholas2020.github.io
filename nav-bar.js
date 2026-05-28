document.addEventListener("DOMContentLoaded", function () {
  const nav = `
    <nav>
      <span class="logo">Natasha Nicholas</span>
      <ul>
        <li><a href="index.html">Home</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="projects.html">Projects</a></li>
      </ul>
      <a href="https://www.linkedin.com/in/natasha-nicholas-2245621a8/git" class="nav-linkedin" target="_blank">
        <i class="fa-brands fa-linkedin"></i>
      </a>
    </nav>
  `;
  document.body.insertAdjacentHTML("afterbegin", nav);
});