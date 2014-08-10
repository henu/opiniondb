from django.db import models
from django.contrib.auth.models import User

class LikeMinded(models.Model):
	user = models.ForeignKey(User, related_name='+')
	likeminded = models.ForeignKey(User, related_name='+')
	priority = models.IntegerField()

	def __unicode__(self):
		return self.user.username + ' => ' + self.likeminded.username + ' ' + str(self.priority)

class Topic(models.Model):

	def __unicode__(self):
		if not self.id:
			return 'Topic'
		return 'Topic #' + str(self.id)

class BooleanOpinion(models.Model):
	user = models.ForeignKey(User, related_name='+')
	value = models.BooleanField()
	topic = models.ForeignKey(Topic, related_name='boolean_opinions')

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
	group = models.ForeignKey(TagCloudGroup, related_name='tags')

	def __unicode__(self):
		result = self.name
		if self.group.id:
			result += '/Tag cloud group #' + str(self.group.id)
		return result

class TagCloud(models.Model):
	group = models.ForeignKey(TagCloudGroup, related_name='clouds')

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

