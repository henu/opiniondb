# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify


# ===========
# CORE MODELS
# ===========

class LikeMinded(models.Model):
	user = models.ForeignKey(User, related_name='+')
	likeminded = models.ForeignKey(User, related_name='+')
	priority = models.IntegerField()

	@staticmethod
	def calculateForUser(user):
		other_users = {}
		# Go all opinions of given user through and
		# check what other people think about them.
		boolean_opinions = BooleanOpinion.objects.filter(user=user)
		for opinion in boolean_opinions:
			# Check opinions of others from same topic
			opinions_of_others = BooleanOpinion.objects.exclude(user=user).filter(topic=opinion.topic)
			for opinion2 in opinions_of_others:
				if opinion2.value == opinion.value:
					other_users.setdefault(opinion2.user.username, 0)
					other_users[opinion2.user.username] += 1
				else:
					other_users.setdefault(opinion2.user.username, 0)
					other_users[opinion2.user.username] -= 1
		# Clean old table
		LikeMinded.objects.filter(user=user).delete()
		# Create new table
		priority = 0
		for t in sorted(other_users.items(), key=lambda t: -t[1]):
			likeminded=User.objects.get(username=t[0])
			LikeMinded.objects.create(user=user, likeminded=likeminded, priority=priority)
			priority += 1

	def __unicode__(self):
		return self.user.username + ' => ' + self.likeminded.username + ' ' + str(self.priority)

	class Meta:
		unique_together = ('user', 'likeminded')

class Topic(models.Model):

	def __unicode__(self):
		if not self.id:
			return 'Topic'
		return 'Topic #' + str(self.id)

class BooleanOpinion(models.Model):
	user = models.ForeignKey(User, related_name='+')
	topic = models.ForeignKey(Topic, related_name='boolean_opinions')
	value = models.BooleanField()

	@staticmethod
	def setOpinionForUser(user, topic, value):
		try:
			boolean_opinion = BooleanOpinion.objects.get(user=user, topic=topic)
			boolean_opinion.value = value
			boolean_opinion.save()
		except BooleanOpinion.DoesNotExist:
			boolean_opinion = BooleanOpinion(user=user, topic=topic, value=value)
			try:
				boolean_opinion.save()
			except IntegrityError:
				boolean_opinion = BooleanOpinion.objects.get(user=user, topic=topic)
				boolean_opinion.value = value
				boolean_opinion.save()

	@staticmethod
	def getBestOpinionFor(user, topic):
		"""Returns opinion value (True/False) from
		specific topic that is best match to given
		user. Anonymous user is None.

		If opinion could not be decided, then None
		is returned.
		"""

		# If not anonymous
		if user:
			# Check if user has opinion by himself/herself
			try:
				opinion = BooleanOpinion.objects.filter(topic=topic).get(user=user)
				return opinion.value
			except BooleanOpinion.DoesNotExist:
				pass

			# Go all like-minded users through
			# and check what they think
			likemindeds = LikeMinded.objects.filter(user=user).order_by('priority')
			for likeminded in likemindeds:
				try:
					opinion = BooleanOpinion.objects.filter(topic=topic).get(user=likeminded.likeminded)
					return opinion.value
				except BooleanOpinion.DoesNotExist:
					pass

		# Get average value in case user is anonymous or if
		# nobody of the like-mindeds did not had an opinion.
		opinions = BooleanOpinion.objects.filter(topic=topic)
		if len(opinions) == 0:
			# Unable to decide
			return None
		trues = 0
		for opinion in opinions:
			if opinion.value:
				trues += 1
		return trues*2 >= len(opinions)

	def __unicode__(self):
		result = self.user.username
		result += ' believes that '
		result += unicode(self.topic)
		result += ' is '
		if self.value: result += 'true'
		else: result += 'false'
		return result

	class Meta:
		unique_together = ('user', 'topic')


# ============
# EXTRA MODELS
# ============

class TagCloudGroup(models.Model):
	""" TagCloudGroup is used to retrieve multiple
	clouds that have some specific tag in them.
	"""

	def __unicode__(self):
		if not self.id:
			return 'Tag cloud group'
		return 'Tag cloud group #' + str(self.id)

class Tag(models.Model):
	name = models.CharField(max_length=255)
	slug = models.CharField(max_length=255)
	group = models.ForeignKey(TagCloudGroup, related_name='tags')

	def generateSlug(self):
		"""Forms slug from name.

		If generated slug is not valid, you can call this
		function again and new slug will be generated.
		"""

		# If there is already a slug, then make
		# some number to the end of new slug
		extra_end = ''
		if self.slug:
			m = re.search('-(?P<number>[0-9]+)$', self.slug)
			if m:
				old_num = int(m.groupdict()['number'])
				extra_end = '-' + str(old_num + 1)
			else:
				extra_end = '-0'

		self.slug = slugify(self.name) + extra_end

	def getCloudsFor(self, user):
		"""Returns list of clouds for specific user.
		User can also be None.
		"""
		result = []
		for cloud in self.clouds.all():
			belongs_to_cloud = BooleanOpinion.getBestOpinionFor(user, cloud.topic)
			if belongs_to_cloud:
				result.append(cloud.cloud)
		return result

	def __unicode__(self):
		result = self.name
		if self.group.id:
			result += '/Tag cloud group #' + str(self.group.id)
		return result

	class Meta:
		unique_together = (('name', 'group'), ('slug', 'group'))

class TagCloud(models.Model):
	group = models.ForeignKey(TagCloudGroup, related_name='clouds')

	def addTag(self, tag_name, user):
		topic = self._getTopicForTagExistence(tag_name, None, True)
		BooleanOpinion.setOpinionForUser(user, topic, True)

	def removeTag(self, tag_slug, user):
		topic = self._getTopicForTagExistence(None, tag_slug, False)
		if topic:
			BooleanOpinion.setOpinionForUser(user, topic, False)
			# If everybody think that this tag does not
			# belong to this cloud, then remove the topic.
			if len(topic.boolean_opinions.filter(value=True)) == 0:
				topic.delete()

	def _getTopicForTagExistence(self, tag_name, tag_slug, create_if_does_not_exist):
		"""Returns requested topic. If topic is not
		found, it is either created, or None is returned,
		base on argument "create_if_does_not_exist".
		"""

		# First check if tag already exists in the group.
		if tag_name:
			tags = self.group.tags.filter(name=tag_name)
		elif tag_slug:
			tags = self.group.tags.filter(slug=tag_slug)
		if len(tags) == 0:
			# Tag does not exist, so create it, or give up
			if not create_if_does_not_exist:
				return None
			tag = Tag(name=tag_name, slug='', group=self.group)
			while True:
				tag.generateSlug()
				try:
					tag.save()
					break
				except IntegrityError:
					pass
		else:
			tag = tags[0]

		# Ensure there is topic about this tag belonging to this cloud
		try:
			tag_belongs_to = TagBelongsTo.objects.get(tag=tag, cloud=self)
		except TagBelongsTo.DoesNotExist:
			# Create new topic, or give up
			if not create_if_does_not_exist:
				return None
			topic = Topic()
			topic.save()
			tag_belongs_to = TagBelongsTo(tag=tag, cloud=self, topic=topic)
			try:
				tag_belongs_to.save()
			except IntegrityError:
				topic.delete()
				tag_belongs_to = TagBelongsTo.objects.get(tag=tag, cloud=self)

		return tag_belongs_to.topic

	def getTagsFor(self, user):
		"""Returns list of tags for specific user.
		User can also be None.
		"""
		all_tags = self.tags.all()
		result = []
		for tag_belongs_to in all_tags:
			topic = tag_belongs_to.topic
			opinion_value = BooleanOpinion.getBestOpinionFor(user, topic)
			if opinion_value:
				result.append(tag_belongs_to.tag)
		return result

	def __unicode__(self):
		if not self.id:
			return 'Tag cloud'
		return 'Tag cloud #' + str(self.id)

class TagBelongsTo(models.Model):
	topic = models.OneToOneField(Topic, related_name='tag_belongs_to')
	tag = models.ForeignKey(Tag, related_name='clouds')
	cloud = models.ForeignKey(TagCloud, related_name='tags')

	def __unicode__(self):
		result = '"' + self.tag.name + '" belongs to Tag cloud'
		if self.cloud.id:
			result += ' #' + str(self.cloud.id)
		return result

	class Meta:
		unique_together = ('tag', 'cloud')

@receiver(post_delete, sender=TagBelongsTo)
def post_delete_tag_belongs_to(sender, instance, *args, **kwargs):
	if instance.topic:
		instance.topic.delete()
	# If this was the last cloud that tag belonged to, then delete tag too
	if len(instance.tag.clouds.all()) == 0:
		instance.tag.delete()

