#############################################################
# $Id: broadcom.mk,v 1.8.2.2 2005/07/16 11:58:31 nbd Exp $
#
# Makefile for the proprietary Broadcom drivers
#
#############################################################

# broadcom specific kmod packages
$(eval $(call KMOD_template,DIAG,diag,\
	$(MODULES_DIR)/kernel/drivers/net/diag/diag.o \
))
$(eval $(call KMOD_template,BRCM_WL,brcm-wl,\
	$(MODULES_DIR)/kernel/drivers/net/wl/wl.o \
,CONFIG_WL))
$(eval $(call KMOD_template,BRCM_ET,brcm-et,\
	$(MODULES_DIR)/kernel/drivers/net/et/et.o \
,CONFIG_ET))
$(eval $(call KMOD_template,LP,lp,\
	$(MODULES_DIR)/kernel/drivers/parport/parport.o \
	$(MODULES_DIR)/kernel/drivers/parport/parport_splink.o \
	$(MODULES_DIR)/kernel/drivers/char/lp.o \
,CONFIG_PARPORT,,50,parport parport_splink lp))

LINUX_BINARY_DRIVER_SITE=http://openwrt.org/downloads/sources
# proprietary driver, extracted from Linksys GPL sourcetree WRT54GS 4.70.6
LINUX_BINARY_WL_DRIVER=kernel-binary-wl-0.4.tar.gz
LINUX_BINARY_WL_MD5SUM=0659fa8f1805be6ec03188ef8e1216cc
LINUX_ET_DRIVER=kernel-source-et-0.10.tar.gz
LINUX_ET_MD5SUM=408901f0b3c672ea0f353795391f07f6

$(DL_DIR)/$(LINUX_BINARY_WL_DRIVER):
	$(SCRIPT_DIR)/download.pl $(DL_DIR) $(LINUX_BINARY_WL_DRIVER) $(LINUX_BINARY_WL_MD5SUM) $(LINUX_BINARY_DRIVER_SITE)

$(DL_DIR)/$(LINUX_ET_DRIVER):
	$(SCRIPT_DIR)/download.pl $(DL_DIR) $(LINUX_ET_DRIVER) $(LINUX_ET_MD5SUM) $(LINUX_BINARY_DRIVER_SITE)
	
$(LINUX_DIR)/.depend_done: $(LINUX_DIR)/.drivers-unpacked
$(LINUX_DIR)/.modules_done: $(LINUX_DIR)/.drivers-unpacked

$(LINUX_DIR)/.drivers-unpacked: $(LINUX_DIR)/.unpacked
	-mkdir -p $(BUILD_DIR)
	zcat $(DL_DIR)/$(LINUX_BINARY_WL_DRIVER) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	zcat $(DL_DIR)/$(LINUX_ET_DRIVER) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	# copy binary wlan driver
	mkdir -p $(LINUX_DIR)/drivers/net/{et,wl}
	cp -a $(BUILD_DIR)/wl/*.o $(LINUX_DIR)/drivers/net/wl
	# copy proprietary et source
	cp -a $(BUILD_DIR)/et/* $(LINUX_DIR)/drivers/net/et
	mkdir -p $(LINUX_DIR)/arch/mips/bcm947xx/include/
	cp -a $(BUILD_DIR)/et/*.h $(LINUX_DIR)/arch/mips/bcm947xx/include/
	touch $@

linux-dirclean: drivers-clean

drivers-clean:
	rm -rf $(BUILD_DIR)/{wl,et}
