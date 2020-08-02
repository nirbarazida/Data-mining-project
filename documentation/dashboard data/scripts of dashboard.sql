# users scraped from each website

SELECT websites.name,
       count(*)
FROM users
JOIN websites ON users.website_id = websites.id
GROUP BY website_id;

# Tag Popularity

SELECT t.name tag_name,
       sum(ut.score) tag_score,
       sum(ut.posts) tag_posts
FROM users u
JOIN user_tags ut ON u.id = ut.user_id
JOIN tags t ON t.id = ut.tag_id
JOIN websites web ON web.id = u.website_id
JOIN location loc ON loc.id = u.location_id
WHERE web.name="{{webebsite}}"
GROUP BY tag_name
ORDER BY tag_score DESC
LIMIT {{Number OF Tags}};

# Tag Popularity By Continent

SELECT location.continent continent,
       tags.name tag_name,
       sum(user_tags.score) tag_score,
       sum(user_tags.posts) tag_posts
FROM users
JOIN user_tags ON users.id = user_tags.user_id
JOIN tags ON tags.id = user_tags.tag_id
JOIN websites ON websites.id = users.website_id
JOIN location ON location.id = users.location_id

WHERE websites.name="{{webebsite}}" and
      location.continent = "{{continent}}"
GROUP BY tags.name
ORDER BY tag_score DESC
Limit 5;

# Top 5 Countries - By Reputation Now

SELECT web.name website_name,
    loc.country country,
    sum(rep.reputation_now) reputation_now
FROM users u
JOIN location loc ON u.location_id = loc.id
JOIN reputation rep ON rep.user_id = u.id
JOIN websites web ON web.id = u.website_id
where web.name="{{webebsite}}" and country != ' '
GROUP BY loc.country
order by reputation_now desc
limit 5;

# User Contribution By Continent

SELECT web.name website_name,
       loc.continent continent,
       count(*) num_users,
       SUM(rep.reputation_now) total_reputation_now,
       SUM(rep.reputation_2020) total_reputation_2020,
       SUM(rep.reputation_2019) total_reputation_2019,
       SUM(rep.reputation_2018) total_reputation_2018,
       SUM(rep.reputation_2017) total_reputation_2017,
       SUM(u.answers) total_answers,
       SUM(u.people_reached) total_people_reached,
       SUM(u.profile_views) total_profile_views
FROM users u
JOIN location loc ON u.location_id = loc.id
JOIN reputation rep ON rep.user_id = u.id
JOIN websites web ON web.id = u.website_id
where web.name="{{website}}"
GROUP BY loc.continent;

# Country Analysis - world map

SELECT websites.name website_name,
       CASE
           WHEN location.country = "United States of America" THEN "United States"
           ELSE location.country
       END AS country,
       sum({{Paramater to analayze}}) as param

FROM users
JOIN location ON users.location_id = location.id
JOIN reputation ON reputation.user_id = users.id
JOIN websites ON websites.id = users.website_id
WHERE websites.name="{{website}}"
GROUP BY location.country;

# number of  users over time

SELECT a.member_since as first,
       count(distinct b.name) as num_users
FROM users a,
     users b
Join websites on websites.id = b.website_id
WHERE a.member_since > b.member_since
  AND a.website_id = b.website_id
  AND websites.name = "{{webebsite}}"
group by a.member_since
ORDER BY a.member_since









