from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class LikeMinded(models.Model):
	user = models.ForeignKey(User, related_name='+')
	likeminded = models.ForeignKey(User, related_name='+')
	priority = models.IntegerField()

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
		if self.value:
			result += ' believes that '
		else:
			result += ' does not believe that '
		result += unicode(self.topic)
		result += ' is true'
		return result

	class Meta:
		unique_together = ('user', 'topic')

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
		# First check if tag already exists in the group.
		# If not, add it there and also slugify it
		tags = self.group.tags.filter(name=tag_name)
		if len(tags) == 0:
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
			topic = Topic()
			topic.save()
			tag_belongs_to = TagBelongsTo(tag=tag, cloud=self, topic=topic)
			try:
				tag_belongs_to.save()
			except IntegrityError:
				topic.delete()
				tag_belongs_to = TagBelongsTo.objects.get(tag=tag, cloud=self)

		BooleanOpinion.setOpinionForUser(user, tag_belongs_to.topic, True)

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

