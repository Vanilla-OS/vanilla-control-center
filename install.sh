VERSION=$(cat VERSION)
dpkg-buildpackage
sudo dpkg -i ../vanilla-control-center_${VERSION}_amd64.deb
vanilla-control-center