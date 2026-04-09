"""
ParentingSimple Auto Post Generator
Generates SEO-optimized parenting articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for parenting
TOPIC_POOLS = {
    "newborn": [
        "How to Get Your Baby to Sleep Through the Night",
        "Newborn Feeding Schedule: Breastfeeding vs Formula in {year}",
        "{number} Essential Items Every New Parent Needs",
        "How to Soothe a Colicky Baby: Proven Methods",
        "Baby Sleep Training Methods Compared: Which One Works",
        "First-Time Parent Survival Guide for the First {number} Weeks",
        "How to Create the Perfect Nursery on a Budget",
        "Signs Your Newborn Is Getting Enough Milk",
        "Baby Milestones: What to Expect in the First Year",
        "How to Establish a Bedtime Routine for Your Baby",
    ],
    "toddler": [
        "Fun Educational Activities for Toddlers at Home",
        "How to Handle Tantrums Without Losing Your Mind",
        "Potty Training Tips That Actually Work in {year}",
        "{number} Screen-Free Activities to Keep Toddlers Busy",
        "Best Educational Toys for Toddlers in {year}",
        "How to Get Your Picky Toddler to Eat Vegetables",
        "Toddler Speech Development: When to Worry",
        "{number} Easy Sensory Play Ideas for Toddlers",
        "How to Transition Your Toddler from Crib to Bed",
        "Gentle Discipline Techniques for Toddlers",
    ],
    "school_age": [
        "Screen Time Rules for Kids: A Parent's Guide {year}",
        "How to Help Your Child Make Friends at School",
        "Best Educational Apps for Kids in {year}",
        "{number} Ways to Make Homework Less Stressful",
        "How to Build Your Child's Confidence and Self-Esteem",
        "After-School Routine Ideas That Reduce Stress",
        "How to Talk to Your Kids About Bullying",
        "Best Books for Kids Ages {number} to 10",
        "How to Encourage a Growth Mindset in Your Child",
        "Fun Science Experiments to Do at Home with Kids",
    ],
    "teen": [
        "How to Talk to Your Teenager About Hard Topics",
        "Setting Boundaries with Teens Without Causing Conflict",
        "{number} Ways to Stay Connected with Your Teenager",
        "Social Media Safety Tips Every Parent Should Know in {year}",
        "How to Help Your Teen Deal with Peer Pressure",
        "Teen Mental Health: Warning Signs Parents Should Watch For",
        "How to Prepare Your Teenager for College and Beyond",
        "Teaching Teenagers About Money and Financial Responsibility",
        "How to Handle Teen Attitude with Grace and Patience",
        "Helping Your Teen Choose the Right Extracurricular Activities",
    ],
    "family_activities": [
        "{number} Fun Family Activities for the Weekend",
        "Budget-Friendly Family Vacation Ideas in {year}",
        "How to Start a Family Game Night Tradition",
        "Best Outdoor Activities for Families with Kids",
        "{number} Creative Rainy Day Activities for the Whole Family",
        "How to Plan the Perfect Family Movie Night",
        "Family Volunteer Ideas That Teach Kids Compassion",
        "Easy Family Meal Prep Ideas for Busy Weeknights",
        "How to Create Meaningful Family Traditions",
        "Best Board Games for Family Night in {year}",
    ],
    "parenting_tips": [
        "Positive Parenting Techniques That Actually Work",
        "How to Stop Yelling at Your Kids: A Step-by-Step Guide",
        "{number} Morning Routine Hacks for Busy Parents",
        "How to Balance Work and Family Life in {year}",
        "Co-Parenting Tips for a Healthier Family Dynamic",
        "Self-Care Ideas for Exhausted Parents",
        "How to Set Effective Rules and Consequences for Kids",
        "Minimalist Parenting: Doing More with Less",
        "How to Raise Kind and Empathetic Children",
        "{number} Parenting Books Every Mom and Dad Should Read",
    ],
    "child_health": [
        "Healthy Lunch Ideas for Kids That They Will Actually Eat",
        "How to Boost Your Child's Immune System Naturally",
        "{number} Healthy Snack Ideas for Kids After School",
        "How Much Sleep Does Your Child Really Need in {year}",
        "Kids and Sugar: How to Reduce Sugar Intake Without Battles",
        "How to Get Your Kids to Exercise and Stay Active",
        "Common Childhood Allergies Every Parent Should Know About",
        "Mental Health Activities for Kids: Building Resilience Early",
        "How to Create a Healthy Meal Plan for Your Family",
        "Best Vitamins and Supplements for Kids in {year}",
    ],
}

SYSTEM_PROMPT = """You are an expert parenting writer for a blog called ParentingSimple.
Write SEO-optimized, informative, and engaging blog posts about parenting and child care.

Rules:
- Write in a warm, supportive, and conversational tone
- Use short paragraphs (2-3 sentences max)
- Include practical, actionable advice parents can use today
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are an experienced parent and child development expert sharing knowledge
- Make content evergreen where possible
- Include specific examples and real-life scenarios
- Be encouraging and non-judgmental
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        # If all attempts hit duplicates, add a random suffix
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Practical parenting tips and advice for raising happy, healthy kids."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename

if __name__ == '__main__':
    # Every 5th post: generate a Gumroad promo post
    from promo_post import should_write_promo, create_promo_post
    if should_write_promo():
        print("Generating promotional post...")
        filepath, filename = create_promo_post()
    else:
        filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
