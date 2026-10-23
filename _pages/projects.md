---
layout: page
title: Projects
permalink: /projects/
description: Selected work
nav: true
nav_order: 2
---
<div class="np">
<header class="np-masthead">
<h1 class="np-title">Projects</h1>
<div class="np-dateline">
<span>Selected work</span>
<span class="np-dateline-mid">Natasha Nicholas</span>
<span>{{ site.time | date: "%B %Y" }}</span>
</div>
</header>
{% assign projects = site.projects | sort: "importance" %}
{% assign lead = projects.first %}
<article class="np-lead{% unless lead.img %} np-lead--text{% endunless %}">
<div class="np-lead-text">
<p class="np-kicker">{{ lead.tech }}</p>
<h2 class="np-headline"><a href="{{ lead.url | relative_url }}">{{ lead.title }}</a></h2>
<p class="np-summary">{{ lead.summary }}</p>
<a class="np-read" href="{{ lead.url | relative_url }}">Read the full story</a>
<blockquote class="np-quote">“I enjoy approaching technical challenges from multiple angles.”</blockquote>
</div>
{% if lead.img %}
<figure class="np-lead-img"><img src="{{ lead.img | relative_url }}" alt="{{ lead.title }}"></figure>
{% endif %}
</article>
<h2 class="np-section">More projects</h2>
<div class="np-grid">
{% for project in projects offset:1 %}
<article class="np-story">
<p class="np-kicker">{{ project.tech }}</p>
<h3 class="np-story-title"><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h3>
<p>{{ project.description }}</p>
<a class="np-read" href="{{ project.url | relative_url }}">Read more</a>
</article>
{% endfor %}
</div>
</div>
