from opiniondb.models import LikeMinded
from opiniondb.models import Topic
from opiniondb.models import BooleanOpinion
from opiniondb.models import TagCloudGroup
from opiniondb.models import Tag
from opiniondb.models import TagCloud
from opiniondb.models import TagBelongsTo

from django.contrib import admin

admin.site.register(LikeMinded)
admin.site.register(Topic)
admin.site.register(BooleanOpinion)
admin.site.register(TagCloudGroup)
admin.site.register(Tag)
admin.site.register(TagCloud)
admin.site.register(TagBelongsTo)

