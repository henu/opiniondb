OpinionDB
=========

OpinionDB is a database like Django library. It's main purpose is to store information. Unlike traditional database, OpinionDB can have many states at the same time. To be precise, it has one for each user plus one for anonymous user.

Users can modify values in database to represent their own views. If user hasn't defined what he/she thinks about some piece of information, OpinionDB tries to guess. It's notable, that this isn't a democratic decision, i.e. the guessing isn't based on average value of all users. Instead OpinionDB keeps track of who have same kind of opinions and uses their decisions when making a guess.

The idea of OpinionDB is to help create political websites and tools. For example, in many comment systems you can rate comments of other users. The problem is, that some people give down votes if they disagree, even if the comment really has a good point.

OpinionDB does not let two fighting groups to mess with each others. Instead it isolates them in two separate groups and offers pleasant "truth" for both parties :)

Datatypes
=========

Datatypes are methods how information is stored. They are divided into two groups: Core and Extra. Core types are simple, fast and universal. For example all of them use the same model named Topic, that represents the subject of information that is being debated on. Extra types are complex and slow and often suitable for only particular use case.

Currently OpinionDB has only one types in both groups.

Core types
----------

### BooleanOpinion

This contains true/false value. In the example below, "user" thinks that "topic" is true.

```BooleanOpinion.setOpinionForUser(user, topic, True)```

Extra types
-----------

### TagCloud

Tag cloud system consists of three parts:

1. Group. This gathers multiple clouds into a tag system. It can be used to find all used tags. There can be many of these, but usually just one is needed.
2. Clouds. These represent entities that can be tagge, for example a news article.
3. Tags. These can be assigned to clouds. Each tag can belong to as many clouds as you want, but only once per cloud.

Here are some usage examples:

```
cloud.addTag('Some tag', user)
cloud.removeTag('another_tag' user)

tags_for_this_cloud = cloud.getTagsFor(user)
tags_from_same_cloud_to_anonymous_user = cloud.getTagsFor(None)

some_tag = tags_for_this_cloud[0]

clouds_where_this_tag_belongs_to = some_tag.getCloudsFor(user)

all_tags_of_group = group.getAllTagsAndCountsFor(user)
all_tags_of_group_for_anonymous_user = group.getAllTagsAndCountsFor(None)
```
