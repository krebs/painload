FROM    ubuntu:latest
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -s /bin/true /sbin/initctl
RUN apt-get update
RUN apt-get install -y python-software-properties python g++ make
RUN add-apt-repository -y ppa:chris-lea/node.js
RUN apt-get update
RUN apt-get -y install nodejs
Add mediengewitter/ /mediengewitter
RUN cd /mediengewitter && npm install 
# -v /media/ext/magnet_pics/:/images
EXPOSE 8080
ENV PORT 8080
RUN rm /mediengewitter/public/content -r
RUN ln -s /images /mediengewitter/public/content
CMD ["/mediengewitter/run.sh"]
