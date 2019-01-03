# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from opiniondb.models import LikeMinded

from django.core.management.base import BaseCommand

class Command(BaseCommand):
	args = '[username1] [username2] ...'
	help = 'Manually calculates likeminded table for specific or all users.'

	def handle(self, *args, **options):

		if len(args) > 0:
			users = User.objects.filter(username__in=args)
		else:
			users = User.objects.all()

		for user in users:
			print 'Calculating for ' + user.username
			LikeMinded.calculateForUser(user)
