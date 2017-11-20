# $Id: Makefile,v 1.3.2.1 2005/08/26 05:20 $

include $(TOPDIR)/rules.mk

PKG_NAME:=bwm-ng
PKG_VERSION:=0.5
PKG_RELEASE:=1
PKG_MD5SUM:=4c5197527c985dc8b45973dfd00deca0

PKG_SOURCE_URL:=http://www.gropp.org/bwm-ng
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_INSTALL_DIR:=$(PKG_BUILD_DIR)/ipkg-install
PKG_CAT:=zcat


include $(TOPDIR)/package/rules.mk

$(eval $(call PKG_template,BWM-NG,$(PKG_NAME),$(PKG_VERSION)-$(PKG_RELEASE),$(ARCH)))

$(PKG_BUILD_DIR)/.configured: $(PKG_BUILD_DIR)/.prepared
	(cd $(PKG_BUILD_DIR); \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS)" \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--sysconfdir=/etc \
		--with-procnetdev \
		--without-strip \
	);
	touch $@

$(PKG_BUILD_DIR)/.built:
	rm -rf $(PKG_INSTALL_DIR)
	mkdir -p $(PKG_INSTALL_DIR)
	$(MAKE) -C $(PKG_BUILD_DIR) \
		$(TARGET_CONFIGURE_OPTS) \
		prefix="$(PKG_INSTALL_DIR)" \
		all install
	touch $@

$(IPKG_BWM-NG):
	mkdir -p $(IDIR_BWM-NG)/usr/bin
	install -m 755 $(PKG_INSTALL_DIR)/bin/$(PKG_NAME) $(IDIR_BWM-NG)/usr/bin/
	$(STRIP) $(IDIR_BWM-NG)/usr/bin/*
	$(IPKG_BUILD) $(IDIR_BWM-NG) $(PACKAGE_DIR)


mostlyclean:
	make -C $(PKG_BUILD_DIR) clean
	rm $(PKG_BUILD_DIR)/.built

