from django.shortcuts import render
from ircarchive.base.models import Channel


def index(request):
    channels = [channel for channel in Channel.all().order('channel')
                    if channel.channel.startswith('#')]
    return render(request, 'base/index.html', {
        'channels': channels,
        })
