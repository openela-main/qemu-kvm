%global libfdt_version 1.6.0
%global libseccomp_version 2.4.0
%global libusbx_version 1.0.23
%global meson_version 0.61.3
%global usbredir_version 0.7.1
%global ipxe_version 20200823-5.git4bd064de

# LTO does not work with the coroutines of QEMU on non-x86 architectures
# (see BZ 1952483 and 1950192 for more information)
%ifnarch x86_64
    %global _lto_cflags %%{nil}
%endif

%global have_usbredir 1
%global have_opengl   1
%global have_fdt      1
%global have_modules_load 0
%global have_memlock_limits 0
# Some of these are not relevant for RHEL, but defining them
# makes it easier to sync the dependency list with Fedora
%global have_block_rbd 1
%global enable_werror 1
%global have_clang 1
%global have_safe_stack 0


%if %{have_clang}
%global toolchain clang
%ifarch x86_64
%global have_safe_stack 1
%endif
%else
%global toolchain gcc
%global cc_suffix .gcc
%endif



# Release candidate version tracking
# global rcver rc4
%if 0%{?rcver:1}
%global rcrel .%{rcver}
%global rcstr -%{rcver}
%endif

# Features disabled in RHEL 10
%global have_pmem 0
%global have_librdma 0

%global have_numactl 1
%ifarch s390x
    %global have_numactl 0
%endif

%global tools_only 0
%ifarch %{power64}
    %global tools_only 1
%endif

%ifnarch x86_64 aarch64
    %global have_usbredir 0
%endif


%global modprobe_kvm_conf %{_sourcedir}/kvm.conf
%ifarch s390x
    %global modprobe_kvm_conf %{_sourcedir}/kvm-s390x.conf
%endif
%ifarch x86_64
    %global modprobe_kvm_conf %{_sourcedir}/kvm-x86.conf
%endif

%ifarch x86_64
    %global kvm_target    x86_64
%else
    %global have_opengl  0
%endif
%ifarch %{power64}
    %global kvm_target    ppc64
    %global have_memlock_limits 1
%endif
%ifarch s390x
    %global kvm_target    s390x
    %global have_modules_load 1
%endif
%ifarch aarch64
    %global kvm_target    aarch64
%endif
%ifarch riscv64
    %global kvm_target    riscv64
%endif


%global target_list %{kvm_target}-softmmu
%global block_drivers_rw_list qcow2,raw,file,host_device,nbd,iscsi,rbd,blkdebug,luks,null-co,nvme,copy-on-read,throttle,compress,virtio-blk-vhost-vdpa,virtio-blk-vfio-pci,virtio-blk-vhost-user,io_uring,nvme-io_uring
%global block_drivers_ro_list vdi,vmdk,vhdx,vpc,https
%define qemudocdir %{_docdir}/%{name}
%global firmwaredirs "%{_datadir}/qemu-firmware:%{_datadir}/ipxe/qemu:%{_datadir}/seavgabios:%{_datadir}/seabios"

#Versions of various parts:

%global requires_all_modules                                     \
%if %{have_opengl}                                               \
Requires: %{name}-ui-opengl = %{epoch}:%{version}-%{release}     \
Requires: %{name}-ui-egl-headless = %{epoch}:%{version}-%{release}     \
%endif                                                           \
Requires: %{name}-device-display-virtio-gpu = %{epoch}:%{version}-%{release}   \
%ifarch s390x                                                    \
Requires: %{name}-device-display-virtio-gpu-ccw = %{epoch}:%{version}-%{release}   \
%else                                                            \
Requires: %{name}-device-display-virtio-gpu-pci = %{epoch}:%{version}-%{release}   \
%endif                                                           \
%ifarch x86_64 %{power64}                                        \
Requires: %{name}-device-display-virtio-vga = %{epoch}:%{version}-%{release}   \
%endif                                                           \
Requires: %{name}-device-usb-host = %{epoch}:%{version}-%{release}   \
%if %{have_usbredir}                                             \
Requires: %{name}-device-usb-redirect = %{epoch}:%{version}-%{release}   \
%endif                                                           \
Requires: %{name}-block-blkio = %{epoch}:%{version}-%{release}   \
%if %{have_block_rbd} \
Requires: %{name}-block-rbd = %{epoch}:%{version}-%{release}     \
%endif \
Requires: %{name}-audio-pa = %{epoch}:%{version}-%{release}

# Since SPICE is removed from RHEL-9, the following Obsoletes:
# removes {name}-ui-spice for upgrades from RHEL-8
# The "<= {version}" assumes RHEL-9 version >= RHEL-8 version (in
# other words RHEL-9 rebases are done together/before RHEL-8 ones)

# In addition, we obsolete some block drivers as we are no longer support
# them in default qemu-kvm installation.

# Note: ssh driver wasn't removed yet just disabled due to late handling

%global obsoletes_some_modules                                  \
Obsoletes: %{name}-ui-spice <= %{epoch}:%{version}                       \
Obsoletes: %{name}-block-gluster <= %{epoch}:%{version}                  \
Obsoletes: %{name}-block-iscsi <= %{epoch}:%{version}                    \
Obsoletes: %{name}-block-ssh <= %{epoch}:%{version}                    \


Summary: QEMU is a machine emulator and virtualizer
Name: qemu-kvm
Version: 10.0.0
Release: 14%{?rcrel}%{?dist}%{?cc_suffix}
# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
# Epoch 15 used for RHEL 8
# Epoch 17 used for RHEL 9 (due to release versioning offset in RHEL 8.5)
Epoch: 18
License: GPL-2.0-only AND GPL-2.0-or-later AND CC-BY-3.0
URL: http://www.qemu.org/
ExclusiveArch: x86_64 %{power64} aarch64 s390x riscv64


Source0: http://wiki.qemu.org/download/qemu-%{version}%{?rcstr}.tar.xz

Source10: qemu-guest-agent.service
Source11: 99-qemu-guest-agent.rules
Source12: bridge.conf
Source13: qemu-ga.sysconfig
Source21: modules-load.conf
Source26: vhost.conf
Source27: kvm.conf
Source28: 95-kvm-memlock.conf
Source30: kvm-s390x.conf
Source31: kvm-x86.conf
Source36: README.tests


Patch0004: 0004-Initial-redhat-build.patch
Patch0005: 0005-Enable-disable-devices-for-RHEL.patch
Patch0006: 0006-Machine-type-related-general-changes.patch
Patch0007: 0007-meson-temporarily-disable-Wunused-function.patch
Patch0008: 0008-Remove-upstream-machine-types-for-aarch64-s390x-and-.patch
Patch0009: 0009-Adapt-versioned-machine-type-macros-for-RHEL.patch
Patch0010: 0010-Increase-deletion-schedule-to-4-releases.patch
Patch0011: 0011-Add-downstream-aarch64-versioned-virt-machine-types.patch
Patch0012: 0012-Add-downstream-s390x-versioned-s390-ccw-virtio-machi.patch
Patch0013: 0013-Add-downstream-x86_64-versioned-pc-q35-machine-types.patch
Patch0014: 0014-Revert-meson-temporarily-disable-Wunused-function.patch
Patch0015: 0015-Enable-make-check.patch
Patch0016: 0016-vfio-cap-number-of-devices-that-can-be-assigned.patch
Patch0017: 0017-Add-support-statement-to-help-output.patch
Patch0018: 0018-Use-qemu-kvm-in-documentation-instead-of-qemu-system.patch
Patch0019: 0019-qcow2-Deprecation-warning-when-opening-v2-images-rw.patch
# For RHEL-87642 - QEMU sends unaligned discards on 4K devices[RHEL-10]
Patch20: kvm-file-posix-probe-discard-alignment-on-Linux-block-de.patch
# For RHEL-87642 - QEMU sends unaligned discards on 4K devices[RHEL-10]
Patch21: kvm-block-io-skip-head-tail-requests-on-EINVAL.patch
# For RHEL-87642 - QEMU sends unaligned discards on 4K devices[RHEL-10]
Patch22: kvm-file-posix-Fix-crash-on-discard_granularity-0.patch
# For RHEL-86056 - Enable 'vhost-user-gpu-pci' in qemu-kvm for RHIVOS
Patch23: kvm-Enable-vhost-user-gpu-pci-for-RHIVOS.patch
# For RHEL-85635 - Video stuck about 1 min after switchover phase when play one video during postcopy-preempt migration
Patch24: kvm-migration-postcopy-Spatial-locality-page-hint-for-pr.patch
# For RHEL-88457 - qemu inadvertantly built with valgrind coroutine stack debugging on x86_64
Patch25: kvm-meson-configure-add-valgrind-option-en-dis-able-valg.patch
# Fixing s390x build issues
Patch26: kvm-docs-Don-t-define-duplicate-label-in-qemu-block-driv.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch27: kvm-block-Expand-block-status-mode-from-bool-to-flags.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch28: kvm-file-posix-gluster-Handle-zero-block-status-hint-bet.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch29: kvm-block-Let-bdrv_co_is_zero_fast-consolidate-adjacent-.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch30: kvm-block-Add-new-bdrv_co_is_all_zeroes-function.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch31: kvm-iotests-Improve-iotest-194-to-mirror-data.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch32: kvm-mirror-Minor-refactoring.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch33: kvm-mirror-Pass-full-sync-mode-rather-than-bool-to-inter.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch34: kvm-mirror-Allow-QMP-override-to-declare-target-already-.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch35: kvm-mirror-Drop-redundant-zero_target-parameter.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch36: kvm-mirror-Skip-pre-zeroing-destination-if-it-is-already.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch37: kvm-mirror-Skip-writing-zeroes-when-target-is-already-ze.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch38: kvm-iotests-common.rc-add-disk_usage-function.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch39: kvm-tests-Add-iotest-mirror-sparse-for-recent-patches.patch
# For RHEL-88435 - --migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1]
# For RHEL-88437 - Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1]
Patch40: kvm-mirror-Reduce-I-O-when-destination-is-detect-zeroes-.patch
# For RHEL-65852 - Support multipath failover with scsi-block
Patch41: kvm-file-posix-Define-DM_MPATH_PROBE_PATHS.patch
# For RHEL-65852 - Support multipath failover with scsi-block
Patch42: kvm-file-posix-Probe-paths-and-retry-SG_IO-on-potential-.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch43: kvm-io-Fix-partial-struct-copy-in-qio_dns_resolver_looku.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch44: kvm-util-qemu-sockets-Refactor-setting-client-sockopts-i.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch45: kvm-util-qemu-sockets-Refactor-success-and-failure-paths.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch46: kvm-util-qemu-sockets-Add-support-for-keep-alive-flag-to.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch47: kvm-util-qemu-sockets-Refactor-inet_parse-to-use-QemuOpt.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch48: kvm-util-qemu-sockets-Introduce-inet-socket-options-cont.patch
# For RHEL-67706 - postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S'
Patch49: kvm-tests-unit-test-util-sockets-fix-mem-leak-on-error-o.patch
# For RHEL-71962 - [RFE] Implement FUA support in scsi-disk
Patch50: kvm-scsi-disk-Add-native-FUA-write-support.patch
# For RHEL-96057 - qemu-kvm: Various small issues in the spec file
Patch51: kvm-Disable-virtio-net-pci-romfile-loading-on-riscv64.patch
# For RHEL-98555 - [s390x][RHEL10.1][ccw-device] there would be memory leak with virtio_blk disks
Patch52: kvm-s390x-Fix-leak-in-machine_set_loadparm.patch
# For RHEL-98555 - [s390x][RHEL10.1][ccw-device] there would be memory leak with virtio_blk disks
Patch53: kvm-hw-s390x-ccw-device-Fix-memory-leak-in-loadparm-sett.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch54: kvm-target-i386-Update-EPYC-CPU-model-for-Cache-property.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch55: kvm-target-i386-Update-EPYC-Rome-CPU-model-for-Cache-pro.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch56: kvm-target-i386-Update-EPYC-Milan-CPU-model-for-Cache-pr.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch57: kvm-target-i386-Add-couple-of-feature-bits-in-CPUID_Fn80.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch58: kvm-target-i386-Update-EPYC-Genoa-for-Cache-property-per.patch
# For RHEL-52650 - [AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model
Patch59: kvm-target-i386-Add-support-for-EPYC-Turin-model.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch60: kvm-include-qemu-compiler-add-QEMU_UNINITIALIZED-attribu.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch61: kvm-hw-virtio-virtio-avoid-cost-of-ftrivial-auto-var-ini.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch62: kvm-block-skip-automatic-zero-init-of-large-array-in-ioq.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch63: kvm-chardev-char-fd-skip-automatic-zero-init-of-large-ar.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch64: kvm-chardev-char-pty-skip-automatic-zero-init-of-large-a.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch65: kvm-chardev-char-socket-skip-automatic-zero-init-of-larg.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch66: kvm-hw-audio-ac97-skip-automatic-zero-init-of-large-arra.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch67: kvm-hw-audio-cs4231a-skip-automatic-zero-init-of-large-a.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch68: kvm-hw-audio-es1370-skip-automatic-zero-init-of-large-ar.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch69: kvm-hw-audio-gus-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch70: kvm-hw-audio-marvell_88w8618-skip-automatic-zero-init-of.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch71: kvm-hw-audio-sb16-skip-automatic-zero-init-of-large-arra.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch72: kvm-hw-audio-via-ac97-skip-automatic-zero-init-of-large-.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch73: kvm-hw-char-sclpconsole-lm-skip-automatic-zero-init-of-l.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch74: kvm-hw-dma-xlnx_csu_dma-skip-automatic-zero-init-of-larg.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch75: kvm-hw-display-vmware_vga-skip-automatic-zero-init-of-la.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch76: kvm-hw-hyperv-syndbg-skip-automatic-zero-init-of-large-a.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch77: kvm-hw-misc-aspeed_hace-skip-automatic-zero-init-of-larg.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch78: kvm-hw-net-rtl8139-skip-automatic-zero-init-of-large-arr.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch79: kvm-hw-net-tulip-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch80: kvm-hw-net-virtio-net-skip-automatic-zero-init-of-large-.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch81: kvm-hw-net-xgamc-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch82: kvm-hw-nvme-ctrl-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch83: kvm-hw-ppc-pnv_occ-skip-automatic-zero-init-of-large-str.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch84: kvm-hw-ppc-spapr_tpm_proxy-skip-automatic-zero-init-of-l.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch85: kvm-hw-usb-hcd-ohci-skip-automatic-zero-init-of-large-ar.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch86: kvm-hw-scsi-lsi53c895a-skip-automatic-zero-init-of-large.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch87: kvm-hw-scsi-megasas-skip-automatic-zero-init-of-large-ar.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch88: kvm-hw-ufs-lu-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch89: kvm-net-socket-skip-automatic-zero-init-of-large-array.patch
# For RHEL-95479 - -ftrivial-auto-var-init=zero reduced performance
Patch90: kvm-net-stream-skip-automatic-zero-init-of-large-array.patch
# For RHEL-85649 - [RHEL 10]Qemu/amd-iommu: Add ability to manually specify the AMDVI-PCI device
Patch91: kvm-hw-i386-amd_iommu-Isolate-AMDVI-PCI-from-amd-iommu-d.patch
# For RHEL-85649 - [RHEL 10]Qemu/amd-iommu: Add ability to manually specify the AMDVI-PCI device
Patch92: kvm-hw-i386-amd_iommu-Allow-migration-when-explicitly-cr.patch
# For RHEL-85649 - [RHEL 10]Qemu/amd-iommu: Add ability to manually specify the AMDVI-PCI device
Patch93: kvm-Enable-amd-iommu-device.patch
# For RHEL-83883 - Video stuck after switchover phase when play one video during migration
Patch94: kvm-ui-vnc-Update-display-update-interval-when-VM-state-.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch95: kvm-migration-multifd-move-macros-to-multifd-header.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch96: kvm-migration-refactor-channel-discovery-mechanism.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch97: kvm-migration-Add-save_postcopy_prepare-savevm-handler.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch98: kvm-migration-ram-Implement-save_postcopy_prepare.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch99: kvm-tests-qtest-migration-consolidate-set-capabilities.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch100: kvm-migration-write-zero-pages-when-postcopy-enabled.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch101: kvm-migration-enable-multifd-and-postcopy-together.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch102: kvm-migration-Add-qtest-for-migration-over-RDMA.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch103: kvm-qtest-migration-rdma-Enforce-RLIMIT_MEMLOCK-128MB-re.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch104: kvm-qtest-migration-rdma-Add-test-for-rdma-migration-wit.patch
# For RHEL-59697 - Allow multifd+postcopy features being enabled together, but only use multifd during precopy 
Patch105: kvm-tests-qtest-migration-add-postcopy-tests-with-multif.patch
# For RHEL-96854 - Performance Degradation(aio=threads) between Upstream Commit b75c5f9 and 984a32f
Patch106: kvm-file-posix-Fix-aio-threads-performance-regression-af.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch107: kvm-block-remove-outdated-comments-about-AioContext-lock.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch108: kvm-block-move-drain-outside-of-read-locked-bdrv_reopen_.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch109: kvm-block-snapshot-move-drain-outside-of-read-locked-bdr.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch110: kvm-block-move-drain-outside-of-read-locked-bdrv_inactiv.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch111: kvm-block-mark-bdrv_parent_change_aio_context-GRAPH_RDLO.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch112: kvm-block-mark-change_aio_ctx-callback-and-instances-as-.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch113: kvm-block-mark-bdrv_child_change_aio_context-GRAPH_RDLOC.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch114: kvm-block-move-drain-outside-of-bdrv_change_aio_context-.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch115: kvm-block-move-drain-outside-of-bdrv_try_change_aio_cont.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch116: kvm-block-move-drain-outside-of-bdrv_attach_child_common.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch117: kvm-block-move-drain-outside-of-bdrv_set_backing_hd_drai.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch118: kvm-block-move-drain-outside-of-bdrv_root_attach_child.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch119: kvm-block-move-drain-outside-of-bdrv_attach_child.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch120: kvm-block-move-drain-outside-of-quorum_add_child.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch121: kvm-block-move-drain-outside-of-bdrv_root_unref_child.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch122: kvm-block-move-drain-outside-of-quorum_del_child.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch123: kvm-blockdev-drain-while-unlocked-in-internal_snapshot_a.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch124: kvm-blockdev-drain-while-unlocked-in-external_snapshot_a.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch125: kvm-block-mark-bdrv_drained_begin-and-friends-as-GRAPH_U.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch126: kvm-iotests-graph-changes-while-io-remove-image-file-aft.patch
# For RHEL-88561 - qemu graph deadlock during job-dismiss
Patch127: kvm-iotests-graph-changes-while-io-add-test-case-with-re.patch
# For RHEL-45624 - Deprecate rtl8139 NIC in QEMU
Patch128: kvm-Declare-rtl8139-as-deprecated.patch
# For RHEL-102325 - [qemu] enable variable service for edk2
Patch129: kvm-Enable-uefi-variable-service-for-edk2.patch
# For RHEL-105440 - Openstack guest becomes inaccessible via network when storage network on the hypervisor is disabled/lost [rhel-10.1]
Patch130: kvm-rbd-Fix-.bdrv_get_specific_info-implementation.patch
Patch131: kvm-i386-Remove-unused-parameter-uint32_t-bit-in-feature.patch
Patch132: kvm-target-i386-Print-CPUID-subleaf-info-for-unsupported.patch
Patch133: kvm-qom-reverse-order-of-instance_post_init-calls.patch
Patch134: kvm-target-i386-Remove-AccelCPUClass-cpu_class_init-need.patch
Patch135: kvm-i386-cpu-Consolidate-the-helper-to-get-Host-s-vendor.patch
Patch136: kvm-rocker-do-not-pollute-the-namespace.patch
Patch137: kvm-include-system-Move-exec-memory.h-to-system-memory.h.patch
Patch138: kvm-include-system-Move-exec-address-spaces.h-to-system-.patch
Patch139: kvm-include-system-Move-exec-ioport.h-to-system-ioport.h.patch
Patch140: kvm-include-system-Move-exec-ram_addr.h-to-system-ram_ad.patch
Patch141: kvm-include-system-Move-exec-ramblock.h-to-system-ramblo.patch
Patch142: kvm-linux-headers-Update-to-Linux-v6.15-rc3.patch
Patch143: kvm-linux-headers-update-from-6.15-kvm-next.patch
Patch144: kvm-update-Linux-headers-to-v6.16-rc3.patch
Patch145: kvm-update-Linux-headers-to-KVM-tree-master.patch
Patch146: kvm-i386-Introduce-tdx-guest-object.patch
Patch147: kvm-i386-tdx-Implement-tdx_kvm_type-for-TDX.patch
Patch148: kvm-i386-tdx-Implement-tdx_kvm_init-to-initialize-TDX-VM.patch
Patch149: kvm-i386-tdx-Get-tdx_capabilities-via-KVM_TDX_CAPABILITI.patch
Patch150: kvm-i386-tdx-Introduce-is_tdx_vm-helper-and-cache-tdx_gu.patch
Patch151: kvm-kvm-Introduce-kvm_arch_pre_create_vcpu.patch
Patch152: kvm-i386-tdx-Initialize-TDX-before-creating-TD-vcpus.patch
Patch153: kvm-i386-tdx-Add-property-sept-ve-disable-for-tdx-guest-.patch
Patch154: kvm-i386-tdx-Make-sept_ve_disable-set-by-default.patch
Patch155: kvm-i386-tdx-Wire-CPU-features-up-with-attributes-of-TD-.patch
Patch156: kvm-i386-tdx-Validate-TD-attributes.patch
Patch157: kvm-i386-tdx-Support-user-configurable-mrconfigid-mrowne.patch
Patch158: kvm-i386-tdx-Set-APIC-bus-rate-to-match-with-what-TDX-mo.patch
Patch159: kvm-i386-tdx-Implement-user-specified-tsc-frequency.patch
Patch160: kvm-i386-tdx-load-TDVF-for-TD-guest.patch
Patch161: kvm-i386-tdvf-Introduce-function-to-parse-TDVF-metadata.patch
Patch162: kvm-i386-tdx-Parse-TDVF-metadata-for-TDX-VM.patch
Patch163: kvm-i386-tdx-Don-t-initialize-pc.rom-for-TDX-VMs.patch
Patch164: kvm-i386-tdx-Track-mem_ptr-for-each-firmware-entry-of-TD.patch
Patch165: kvm-i386-tdx-Track-RAM-entries-for-TDX-VM.patch
Patch166: kvm-headers-Add-definitions-from-UEFI-spec-for-volumes-r.patch
Patch167: kvm-i386-tdx-Setup-the-TD-HOB-list.patch
Patch168: kvm-i386-tdx-Add-TDVF-memory-via-KVM_TDX_INIT_MEM_REGION.patch
Patch169: kvm-i386-tdx-Call-KVM_TDX_INIT_VCPU-to-initialize-TDX-vc.patch
Patch170: kvm-i386-tdx-Finalize-TDX-VM.patch
Patch171: kvm-i386-tdx-Enable-user-exit-on-KVM_HC_MAP_GPA_RANGE.patch
Patch172: kvm-i386-tdx-Handle-KVM_SYSTEM_EVENT_TDX_FATAL.patch
Patch173: kvm-i386-tdx-Wire-TDX_REPORT_FATAL_ERROR-with-GuestPanic.patch
Patch174: kvm-kvm-Check-KVM_CAP_MAX_VCPUS-at-vm-level.patch
Patch175: kvm-i386-cpu-introduce-x86_confidential_guest_cpu_instan.patch
Patch176: kvm-i386-tdx-implement-tdx_cpu_instance_init.patch
Patch177: kvm-i386-cpu-Introduce-enable_cpuid_0x1f-to-force-exposi.patch
Patch178: kvm-i386-tdx-Force-exposing-CPUID-0x1f.patch
Patch179: kvm-i386-tdx-Set-kvm_readonly_mem_enabled-to-false-for-T.patch
Patch180: kvm-i386-tdx-Disable-SMM-for-TDX-VMs.patch
Patch181: kvm-i386-tdx-Disable-PIC-for-TDX-VMs.patch
Patch182: kvm-i386-tdx-Set-and-check-kernel_irqchip-mode-for-TDX.patch
Patch183: kvm-i386-tdx-Don-t-synchronize-guest-tsc-for-TDs.patch
Patch184: kvm-i386-tdx-Only-configure-MSR_IA32_UCODE_REV-in-kvm_in.patch
Patch185: kvm-i386-apic-Skip-kvm_apic_put-for-TDX.patch
Patch186: kvm-cpu-Don-t-set-vcpu_dirty-when-guest_state_protected.patch
Patch187: kvm-i386-cgs-Rename-mask_cpuid_features-to-adjust_cpuid_.patch
Patch188: kvm-i386-tdx-Implement-adjust_cpuid_features-for-TDX.patch
Patch189: kvm-i386-tdx-Add-TDX-fixed1-bits-to-supported-CPUIDs.patch
Patch190: kvm-i386-tdx-Add-supported-CPUID-bits-related-to-TD-Attr.patch
Patch191: kvm-i386-tdx-Add-supported-CPUID-bits-relates-to-XFAM.patch
Patch192: kvm-i386-tdx-Add-XFD-to-supported-bit-of-TDX.patch
Patch193: kvm-i386-tdx-Define-supported-KVM-features-for-TDX.patch
Patch194: kvm-i386-cgs-Introduce-x86_confidential_guest_check_feat.patch
Patch195: kvm-i386-tdx-Fetch-and-validate-CPUID-of-TD-guest.patch
Patch196: kvm-i386-tdx-Don-t-treat-SYSCALL-as-unavailable.patch
Patch197: kvm-i386-tdx-Make-invtsc-default-on.patch
Patch198: kvm-i386-tdx-Validate-phys_bits-against-host-value.patch
Patch199: kvm-docs-Add-TDX-documentation.patch
Patch200: kvm-i386-tdx-Fix-build-on-32-bit-host.patch
Patch201: kvm-i386-tdvf-Fix-build-on-32-bit-host.patch
Patch202: kvm-i386-cpu-Move-adjustment-of-CPUID_EXT_PDCM-before-fe.patch
Patch203: kvm-i386-tdx-Error-and-exit-when-named-cpu-model-is-requ.patch
Patch204: kvm-i386-cpu-Rename-enable_cpuid_0x1f-to-force_cpuid_0x1.patch
Patch205: kvm-i386-tdx-Fix-the-typo-of-the-comment-of-struct-TdxGu.patch
Patch206: kvm-i386-tdx-Clarify-the-error-message-of-mrconfigid-mro.patch
Patch207: kvm-i386-tdx-handle-TDG.VP.VMCALL-GetTdVmCallInfo.patch
Patch208: kvm-i386-tdx-handle-TDG.VP.VMCALL-GetQuote.patch
Patch209: kvm-target-i386-move-max_features-to-class.patch
Patch210: kvm-target-i386-nvmm-whpx-add-accel-CPU-class-that-sets-.patch
Patch211: kvm-target-i386-allow-reordering-max_x86_cpu_initfn-vs-a.patch
Patch212: kvm-target-i386-move-accel_cpu_instance_init-to-.instanc.patch
Patch213: kvm-target-i386-merge-host_cpu_instance_init-and-host_cp.patch
Patch214: kvm-i386-tdx-Remove-enumeration-of-GetQuote-in-tdx_handl.patch
Patch215: kvm-i386-tdx-Set-value-of-GetTdVmCallInfo-based-on-capab.patch
Patch216: kvm-i386-tdx-handle-TDVMCALL_SETUP_EVENT_NOTIFY_INTERRUP.patch
Patch217: kvm-i386-tdx-Fix-the-report-of-gpa-in-QAPI.patch
Patch218: kvm-i386-tdx-Remove-task-watch-only-when-it-s-valid.patch
Patch219: kvm-i386-tdx-Don-t-mask-off-CPUID_EXT_PDCM.patch
Patch220: kvm-i386-cpu-Move-x86_ext_save_areas-initialization-to-..patch
Patch221: kvm-target-i386-tdx-fix-locking-for-interrupt-injection.patch
Patch222: kvm-i386-cpu-Cleanup-host_cpu_max_instance_init.patch
Patch223: kvm-i386-tdx-Remove-the-redundant-qemu_mutex_init-tdx-lo.patch
Patch224: kvm-redhat-enable-CONFIG_TDX.patch
Patch225: kvm-redhat-allow-5-level-paging-for-TDX-VMs.patch
Patch226: kvm-memory-Export-a-helper-to-get-intersection-of-a-Memo.patch
Patch227: kvm-memory-Change-memory_region_set_ram_discard_manager-.patch
Patch228: kvm-memory-Unify-the-definiton-of-ReplayRamPopulate-and-.patch
Patch229: kvm-ram-block-attributes-Introduce-RamBlockAttributes-to.patch
Patch230: kvm-physmem-Support-coordinated-discarding-of-RAM-with-g.patch
# For RHEL-108614 - CVE-2025-8860 qemu-kvm: uefi-vars: information disclosure vulnerability in uefi_vars_write callback [rhel-10.1]
Patch231: kvm-hw-uefi-clear-uefi-vars-buffer-in-uefi_vars_write-ca.patch
# For RHEL-108614 - CVE-2025-8860 qemu-kvm: uefi-vars: information disclosure vulnerability in uefi_vars_write callback [rhel-10.1]
Patch232: kvm-hw-uefi-return-success-for-notifications.patch
# For RHEL-108614 - CVE-2025-8860 qemu-kvm: uefi-vars: information disclosure vulnerability in uefi_vars_write callback [rhel-10.1]
Patch233: kvm-hw-uefi-check-access-for-first-variable.patch

%if %{have_clang}
BuildRequires: clang
%if %{have_safe_stack}
BuildRequires: compiler-rt
%endif
%else
BuildRequires: gcc
%endif
BuildRequires: meson >= %{meson_version}
BuildRequires: ninja-build
BuildRequires: zlib-devel
BuildRequires: libzstd-devel
BuildRequires: glib2-devel
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libaio-devel
BuildRequires: libblkio-devel
BuildRequires: liburing-devel
BuildRequires: python3-devel
BuildRequires: libattr-devel
BuildRequires: libusbx-devel >= %{libusbx_version}
%if %{have_usbredir}
BuildRequires: usbredir-devel >= %{usbredir_version}
%endif
BuildRequires: texinfo
BuildRequires: python3-sphinx
BuildRequires: python3-sphinx_rtd_theme
BuildRequires: libseccomp-devel >= %{libseccomp_version}
# For network block driver
BuildRequires: libcurl-devel
%if %{have_block_rbd}
BuildRequires: librbd-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# Required as we use dtrace for trace backend
BuildRequires: /usr/bin/dtrace
# For VNC PNG support
BuildRequires: libpng-devel
# For virtiofs
BuildRequires: libcap-ng-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
# For rdma
%if %{have_librdma}
BuildRequires: rdma-core-devel
%endif
%if %{have_fdt}
BuildRequires: libfdt-devel >= %{libfdt_version}
%endif
# For compressed guest memory dumps
BuildRequires: lzo-devel snappy-devel
# For NUMA memory binding
%if %{have_numactl}
BuildRequires: numactl-devel
%endif
# qemu-pr-helper multipath support (requires libudev too)
BuildRequires: device-mapper-multipath-devel
BuildRequires: systemd-devel
%if %{have_pmem}
BuildRequires: libpmem-devel
%endif
# qemu-keymap
BuildRequires: pkgconfig(xkbcommon)
%if %{have_opengl}
BuildRequires: pkgconfig(epoxy)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(gbm)
%endif
BuildRequires: perl-Test-Harness
BuildRequires: libslirp-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: spice-protocol
BuildRequires: capstone-devel
%ifarch %{valgrind_arches}
BuildRequires: valgrind-devel
%endif

# Requires for qemu-kvm package
Requires: %{name}-core = %{epoch}:%{version}-%{release}
Requires: %{name}-docs = %{epoch}:%{version}-%{release}
Requires: %{name}-tools = %{epoch}:%{version}-%{release}
Requires: qemu-pr-helper = %{epoch}:%{version}-%{release}
Requires: virtiofsd >= 1.5.0
%{requires_all_modules}

%description
%{name} is an open source virtualizer that provides hardware
emulation for the KVM hypervisor. %{name} acts as a virtual
machine monitor together with the KVM kernel modules, and emulates the
hardware for a full system such as a PC and its associated peripherals.


%package core
Summary: %{name} core components
%{obsoletes_some_modules}
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: qemu-img = %{epoch}:%{version}-%{release}
%ifarch x86_64
Requires: edk2-ovmf
%endif
%ifarch aarch64
Requires: edk2-aarch64
%endif
%ifarch riscv64
Requires: edk2-riscv64
%endif

Requires: libseccomp >= %{libseccomp_version}
Requires: libusbx >= %{libusbx_version}
Requires: capstone
%if %{have_fdt}
Requires: libfdt >= %{libfdt_version}
%endif

%description core
%{name} is an open source virtualizer that provides hardware
emulation for the KVM hypervisor. %{name} acts as a virtual
machine monitor together with the KVM kernel modules, and emulates the
hardware for a full system such as a PC and its associated peripherals.
This is a minimalistic installation of %{name}. Functionality provided by
this package is not ensured and it can change in a future version as some
functionality can be split out to separate package.
Before updating this package, it is recommended to check the package
changelog for information on functionality which might have been moved to
a separate package to prevent issues due to the moved functionality.
If apps opt-in to minimalist packaging by depending on %{name}-core, they
explicitly accept that features may disappear from %{name}-core in future
updates.

%package common
Summary: QEMU common files needed by all QEMU targets
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%ifarch x86_64
Requires: seabios-bin >= 1.10.2-1
%endif
%ifarch x86_64 %{power64}
Requires: seavgabios-bin >= 1.12.0-3
Requires: ipxe-roms-qemu >= %{ipxe_version}
%endif
# Removal -gl modules as they do not provide any functionality - see bz#2149022
Obsoletes: %{name}-device-display-virtio-gpu-gl <= %{epoch}:%{version}
Obsoletes: %{name}-device-display-virtio-gpu-pci-gl <= %{epoch}:%{version}
Obsoletes: %{name}-device-display-virtio-vga-gl <= %{epoch}:%{version}

%description common
%{name} is an open source virtualizer that provides hardware emulation for
the KVM hypervisor.

This package provides documentation and auxiliary programs used with %{name}.


%package tools
Summary: %{name} support tools
Recommends: systemtap-client
Recommends: systemtap-devel
%description tools
%{name}-tools provides various tools related to %{name} usage.


%package docs
Summary: %{name} documentation
%description docs
%{name}-docs provides documentation files regarding %{name}.


%package -n qemu-pr-helper
Summary: qemu-pr-helper utility for %{name}
%description -n qemu-pr-helper
This package provides the qemu-pr-helper utility that is required for certain
SCSI features.


%package -n qemu-img
Summary: QEMU command line tool for manipulating disk images
%description -n qemu-img
This package provides a command line tool for manipulating disk images.


%package -n qemu-guest-agent
Summary: QEMU guest agent
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%description -n qemu-guest-agent
%{name} is an open source virtualizer that provides hardware emulation for
the KVM hypervisor.

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.


%package tests
Summary: tests for the %{name} package
Requires: %{name} = %{epoch}:%{version}-%{release}

%define testsdir %{_libdir}/%{name}/tests-src

%description tests
The %{name}-tests rpm contains tests that can be used to verify
the functionality of the installed %{name} package

Install this package if you want access to the avocado_qemu
tests, or qemu-iotests.


%package  block-blkio
Summary: QEMU libblkio block drivers
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-blkio
This package provides the additional libblkio block drivers for QEMU.

Install this package if you want to use virtio-blk-vdpa-blk,
virtio-blk-vfio-pci, virtio-blk-vhost-user, io_uring, and nvme-io_uring block
drivers provided by libblkio.


%package  block-curl
Summary: QEMU CURL block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-curl
This package provides the additional CURL block driver for QEMU.

Install this package if you want to access remote disks over
http, https, ftp and other transports provided by the CURL library.


%if %{have_block_rbd}
%package  block-rbd
Summary: QEMU Ceph/RBD block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-rbd
This package provides the additional Ceph/RBD block driver for QEMU.

Install this package if you want to access remote Ceph volumes
using the rbd protocol.
%endif


%package  audio-pa
Summary: QEMU PulseAudio audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description audio-pa
This package provides the additional PulseAudio audio driver for QEMU.


%if %{have_opengl}
%package  ui-opengl
Summary: QEMU opengl support
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: mesa-libGL
Requires: mesa-libEGL
Requires: mesa-dri-drivers
%description ui-opengl
This package provides opengl support.

%package  ui-egl-headless
Summary: QEMU EGL headless driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-ui-opengl%{?_isa} = %{epoch}:%{version}-%{release}
%description ui-egl-headless
This package provides the additional egl-headless UI for QEMU.
%endif


%package device-display-virtio-gpu
Summary: QEMU virtio-gpu display device
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description device-display-virtio-gpu
This package provides the virtio-gpu display device for QEMU.

%ifarch s390x
%package device-display-virtio-gpu-ccw
Summary: QEMU virtio-gpu-ccw display device
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-device-display-virtio-gpu = %{epoch}:%{version}-%{release}
%description device-display-virtio-gpu-ccw
This package provides the virtio-gpu-ccw display device for QEMU.
%else
%package device-display-virtio-gpu-pci
Summary: QEMU virtio-gpu-pci display device
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-device-display-virtio-gpu = %{epoch}:%{version}-%{release}
%description device-display-virtio-gpu-pci
This package provides the virtio-gpu-pci display device for QEMU.
%endif

%ifarch x86_64 %{power64}
%package device-display-virtio-vga
Summary: QEMU virtio-vga display device
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description device-display-virtio-vga
This package provides the virtio-vga display device for QEMU.
%endif

%package device-usb-host
Summary: QEMU usb host device
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description device-usb-host
This package provides the USB pass through driver for QEMU.

%if %{have_usbredir}
%package  device-usb-redirect
Summary: QEMU usbredir support
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: usbredir >= 0.7.1
Provides: %{name}-hw-usbredir
Obsoletes: %{name}-hw-usbredir <= %{epoch}:%{version}

%description device-usb-redirect
This package provides usbredir support.
%endif

%package  ui-dbus
Summary: QEMU D-Bus UI driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description ui-dbus
This package provides the additional D-Bus UI for QEMU.

%package  audio-dbus
Summary: QEMU D-Bus audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-ui-dbus = %{epoch}:%{version}-%{release}
%description audio-dbus
This package provides the additional D-Bus audio driver for QEMU.

%prep
%setup -q -n qemu-%{version}%{?rcstr}
%autopatch -p1

%global qemu_kvm_build qemu_kvm_build
mkdir -p %{qemu_kvm_build}


%build

# Necessary hack for ZUUL CI
ulimit -n 10240

%define disable_everything         \\\
  --audio-drv-list=                \\\
  --disable-alsa                   \\\
  --disable-asan                   \\\
  --disable-attr                   \\\
  --disable-auth-pam               \\\
  --disable-avx2                   \\\
  --disable-avx512bw               \\\
  --disable-blkio                  \\\
  --disable-block-drv-whitelist-in-tools \\\
  --disable-bochs                  \\\
  --disable-bpf                    \\\
  --disable-brlapi                 \\\
  --disable-bsd-user               \\\
  --disable-bzip2                  \\\
  --disable-cap-ng                 \\\
  --disable-capstone               \\\
  --disable-cfi                    \\\
  --disable-cfi-debug              \\\
  --disable-cloop                  \\\
  --disable-cocoa                  \\\
  --disable-coreaudio              \\\
  --disable-coroutine-pool         \\\
  --disable-crypto-afalg           \\\
  --disable-curl                   \\\
  --disable-curses                 \\\
  --disable-dbus-display           \\\
  --disable-debug-info             \\\
  --disable-debug-mutex            \\\
  --disable-debug-tcg              \\\
  --disable-dmg                    \\\
  --disable-docs                   \\\
  --disable-download               \\\
  --disable-dsound                 \\\
  --disable-fdt                    \\\
  --disable-fuse                   \\\
  --disable-fuse-lseek             \\\
  --disable-gcrypt                 \\\
  --disable-gettext                \\\
  --disable-gio                    \\\
  --disable-glusterfs              \\\
  --disable-gnutls                 \\\
  --disable-gtk                    \\\
  --disable-guest-agent            \\\
  --disable-guest-agent-msi        \\\
  --disable-hvf                    \\\
  --disable-iconv                  \\\
  --disable-jack                   \\\
  --disable-kvm                    \\\
  --disable-l2tpv3                 \\\
  --disable-libdaxctl              \\\
  --disable-libdw                  \\\
  --disable-libiscsi               \\\
  --disable-libnfs                 \\\
  --disable-libpmem                \\\
  --disable-libssh                 \\\
  --disable-libudev                \\\
  --disable-libusb                 \\\
  --disable-libvduse               \\\
  --disable-linux-aio              \\\
  --disable-linux-io-uring         \\\
  --disable-linux-user             \\\
  --disable-lto                    \\\
  --disable-lzfse                  \\\
  --disable-lzo                    \\\
  --disable-malloc-trim            \\\
  --disable-membarrier             \\\
  --disable-modules                \\\
  --disable-module-upgrades        \\\
  --disable-mpath                  \\\
  --disable-multiprocess           \\\
  --disable-netmap                 \\\
  --disable-nettle                 \\\
  --disable-numa                   \\\
  --disable-nvmm                   \\\
  --disable-opengl                 \\\
  --disable-oss                    \\\
  --disable-pa                     \\\
  --disable-parallels              \\\
  --disable-pie                    \\\
  --disable-plugins                \\\
  --disable-pvg                    \\\
  --disable-qcow1                  \\\
  --disable-qed                    \\\
  --disable-qga-vss                \\\
  --disable-qom-cast-debug         \\\
  --disable-rbd                    \\\
  --disable-rdma                   \\\
  --disable-replication            \\\
  --disable-rng-none               \\\
  --disable-safe-stack             \\\
  --disable-sdl                    \\\
  --disable-sdl-image              \\\
  --disable-seccomp                \\\
  --disable-selinux                \\\
  --disable-slirp                  \\\
  --disable-slirp-smbd             \\\
  --disable-smartcard              \\\
  --disable-snappy                 \\\
  --disable-sndio                  \\\
  --disable-sparse                 \\\
  --disable-spice                  \\\
  --disable-spice-protocol         \\\
  --disable-strip                  \\\
  --disable-system                 \\\
  --disable-tcg                    \\\
  --disable-tools                  \\\
  --disable-tpm                    \\\
  --disable-u2f                    \\\
  --disable-ubsan                  \\\
  --disable-usb-redir              \\\
  --disable-user                   \\\
  --disable-valgrind               \\\
  --disable-vde                    \\\
  --disable-vdi                    \\\
  --disable-vduse-blk-export       \\\
  --disable-vhost-crypto           \\\
  --disable-vhost-kernel           \\\
  --disable-vhost-net              \\\
  --disable-vhost-user             \\\
  --disable-vhost-user-blk-server  \\\
  --disable-vhost-vdpa             \\\
  --disable-virglrenderer          \\\
  --disable-virtfs                 \\\
  --disable-vnc                    \\\
  --disable-vnc-jpeg               \\\
  --disable-png                    \\\
  --disable-vnc-sasl               \\\
  --disable-vte                    \\\
  --disable-vvfat                  \\\
  --disable-werror                 \\\
  --disable-whpx                   \\\
  --disable-xen                    \\\
  --disable-xen-pci-passthrough    \\\
  --disable-xkbcommon              \\\
  --disable-zstd                   \\\
  --without-default-devices


run_configure() {
    ../configure \
        --cc=%{__cc} \
        --cxx=/bin/false \
        --prefix="%{_prefix}" \
        --libdir="%{_libdir}" \
        --datadir="%{_datadir}" \
        --sysconfdir="%{_sysconfdir}" \
        --interp-prefix=%{_prefix}/qemu-%M \
        --localstatedir="%{_localstatedir}" \
        --docdir="%{_docdir}" \
        --libexecdir="%{_libexecdir}" \
        --extra-ldflags="%{build_ldflags}" \
        --extra-cflags="%{optflags} -Wno-string-plus-int" \
        --with-pkgversion="%{name}-%{version}-%{release}" \
        --with-suffix="%{name}" \
        --firmwarepath=%{firmwaredirs} \
        --enable-trace-backends=dtrace \
        --with-coroutine=ucontext \
        --tls-priority=@QEMU,SYSTEM \
        %{disable_everything} \
%ifarch aarch64 s390x x86_64 riscv64
        --with-devices-%{kvm_target}=%{kvm_target}-rh-devices \
%endif
	--rhel-version=10 \
        "$@"

    echo "config-host.mak contents:"
    echo "==="
    cat config-host.mak
    echo "==="
}


pushd %{qemu_kvm_build}
run_configure \
%if %{defined target_list}
  --target-list="%{target_list}" \
%endif
%if %{defined block_drivers_rw_list}
  --block-drv-rw-whitelist=%{block_drivers_rw_list} \
%endif
%if %{defined block_drivers_ro_list}
  --block-drv-ro-whitelist=%{block_drivers_ro_list} \
%endif
  --enable-attr \
  --enable-blkio \
  --enable-cap-ng \
  --enable-capstone \
  --enable-coroutine-pool \
  --enable-curl \
  --enable-dbus-display \
  --enable-debug-info \
  --enable-docs \
%if %{have_fdt}
  --enable-fdt=system \
%endif
  --enable-gio \
  --enable-gnutls \
  --enable-guest-agent \
  --enable-iconv \
  --enable-kvm \
%if %{have_pmem}
  --enable-libpmem \
%endif
  --enable-libusb \
  --enable-libudev \
  --enable-linux-aio \
  --enable-linux-io-uring \
  --enable-lzo \
  --enable-malloc-trim \
  --enable-modules \
  --enable-mpath \
%if %{have_numactl}
  --enable-numa \
%endif
%if %{have_opengl}
  --enable-opengl \
%endif
  --enable-pa \
  --enable-pie \
%if %{have_block_rbd}
  --enable-rbd \
%endif
%if %{have_librdma}
  --enable-rdma \
%endif
  --enable-seccomp \
  --enable-selinux \
  --enable-slirp \
  --enable-snappy \
  --enable-spice-protocol \
  --enable-system \
  --enable-tcg \
  --enable-tools \
  --enable-tpm \
%if %{have_usbredir}
  --enable-usb-redir \
%endif
%ifarch %{valgrind_arches}
  --enable-valgrind \
%endif
  --enable-vdi \
  --enable-vhost-kernel \
  --enable-vhost-net \
  --enable-vhost-user \
  --enable-vhost-user-blk-server \
  --enable-vhost-vdpa \
  --enable-vnc \
  --enable-png \
  --enable-vnc-sasl \
%if %{enable_werror}
  --enable-werror \
%endif
  --enable-xkbcommon \
  --enable-zstd \
%if %{have_safe_stack}
  --enable-safe-stack \
%endif

%if %{tools_only}
%make_build qemu-img
%make_build qemu-io
%make_build qemu-nbd
%make_build storage-daemon/qemu-storage-daemon

%make_build docs/qemu-img.1
%make_build docs/qemu-nbd.8
%make_build docs/qemu-storage-daemon.1
%make_build docs/qemu-storage-daemon-qmp-ref.7

%make_build qga/qemu-ga
%make_build docs/qemu-ga.8
# endif tools_only
%endif


%if !%{tools_only}
%make_build

# Setup back compat qemu-kvm binary
%{__python3} scripts/tracetool.py --backend dtrace --format stap \
  --group=all --binary %{_libexecdir}/qemu-kvm --probe-prefix qemu.kvm \
  trace/trace-events-all qemu-kvm.stp

%{__python3} scripts/tracetool.py --backends=dtrace --format=log-stap \
  --group=all --binary %{_libexecdir}/qemu-kvm --probe-prefix qemu.kvm \
  trace/trace-events-all qemu-kvm-log.stp

%{__python3} scripts/tracetool.py --backend dtrace --format simpletrace-stap \
  --group=all --binary %{_libexecdir}/qemu-kvm --probe-prefix qemu.kvm \
  trace/trace-events-all qemu-kvm-simpletrace.stp

cp -a qemu-system-%{kvm_target} qemu-kvm

%ifarch s390x
    # Copy the built new images into place for "make check":
    cp pc-bios/s390-ccw/s390-ccw.img pc-bios/
%endif


popd
# endif !tools_only
%endif



%install
# Install qemu-guest-agent service and udev rules
install -D -m 0644 %{_sourcedir}/qemu-guest-agent.service %{buildroot}%{_unitdir}/qemu-guest-agent.service
install -D -m 0644 %{_sourcedir}/qemu-ga.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/qemu-ga
install -D -m 0644 %{_sourcedir}/99-qemu-guest-agent.rules %{buildroot}%{_udevrulesdir}/99-qemu-guest-agent.rules


# Install qemu-ga fsfreeze bits
mkdir -p %{buildroot}%{_sysconfdir}/qemu-ga/fsfreeze-hook.d
install -p scripts/qemu-guest-agent/fsfreeze-hook %{buildroot}%{_sysconfdir}/qemu-ga/fsfreeze-hook
mkdir -p %{buildroot}%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
install -p -m 0644 scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample %{buildroot}%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
mkdir -p -v %{buildroot}%{_localstatedir}/log/qemu-ga/


%if %{tools_only}
pushd %{qemu_kvm_build}
install -D -p -m 0755 qga/qemu-ga %{buildroot}%{_bindir}/qemu-ga
install -D -p -m 0755 qemu-img %{buildroot}%{_bindir}/qemu-img
install -D -p -m 0755 qemu-io %{buildroot}%{_bindir}/qemu-io
install -D -p -m 0755 qemu-nbd %{buildroot}%{_bindir}/qemu-nbd
install -D -p -m 0755 storage-daemon/qemu-storage-daemon %{buildroot}%{_bindir}/qemu-storage-daemon

mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_mandir}/man7/
mkdir -p %{buildroot}%{_mandir}/man8/

install -D -p -m 644 docs/qemu-img.1* %{buildroot}%{_mandir}/man1
install -D -p -m 644 docs/qemu-nbd.8* %{buildroot}%{_mandir}/man8
install -D -p -m 644 docs/qemu-storage-daemon.1* %{buildroot}%{_mandir}/man1
install -D -p -m 644 docs/qemu-storage-daemon-qmp-ref.7* %{buildroot}%{_mandir}/man7
install -D -p -m 644 docs/qemu-ga.8* %{buildroot}%{_mandir}/man8
popd
# endif tools_only
%endif

%if !%{tools_only}

install -D -p -m 0644 %{_sourcedir}/vhost.conf %{buildroot}%{_sysconfdir}/modprobe.d/vhost.conf
install -D -p -m 0644 %{modprobe_kvm_conf} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/kvm.conf

# Create new directories and put them all under tests-src
mkdir -p %{buildroot}%{testsdir}/python
mkdir -p %{buildroot}%{testsdir}/tests
mkdir -p %{buildroot}%{testsdir}/tests/avocado
mkdir -p %{buildroot}%{testsdir}/tests/qemu-iotests
mkdir -p %{buildroot}%{testsdir}/scripts/qmp


install -m 0644 scripts/dump-guest-memory.py \
                %{buildroot}%{_datadir}/%{name}

# Install avocado_qemu tests
cp -R %{qemu_kvm_build}/tests/avocado/* %{buildroot}%{testsdir}/tests/avocado/

# Install qemu.py and qmp/ scripts required to run avocado_qemu tests
cp -R %{qemu_kvm_build}/python/qemu %{buildroot}%{testsdir}/python
cp -R %{qemu_kvm_build}/scripts/qmp/* %{buildroot}%{testsdir}/scripts/qmp
install -p -m 0644 tests/Makefile.include %{buildroot}%{testsdir}/tests/

# Install qemu-iotests
cp -R tests/qemu-iotests/* %{buildroot}%{testsdir}/tests/qemu-iotests/
cp -ur %{qemu_kvm_build}/tests/qemu-iotests/* %{buildroot}%{testsdir}/tests/qemu-iotests/

install -p -m 0644 %{_sourcedir}/README.tests %{buildroot}%{testsdir}/README

# Do the actual qemu tree install
pushd %{qemu_kvm_build}
%make_install
popd

mkdir -p %{buildroot}%{_datadir}/systemtap/tapset

install -m 0755 %{qemu_kvm_build}/qemu-system-%{kvm_target} %{buildroot}%{_libexecdir}/qemu-kvm
install -m 0644 %{qemu_kvm_build}/qemu-kvm.stp %{buildroot}%{_datadir}/systemtap/tapset/
install -m 0644 %{qemu_kvm_build}/qemu-kvm-log.stp %{buildroot}%{_datadir}/systemtap/tapset/
install -m 0644 %{qemu_kvm_build}/qemu-kvm-simpletrace.stp %{buildroot}%{_datadir}/systemtap/tapset/
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/systemtap/script.d"
install -c -m 0644 %{qemu_kvm_build}/scripts/systemtap/script.d/qemu_kvm.stp "%{buildroot}%{_datadir}/%{name}/systemtap/script.d/"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/systemtap/conf.d"
install -c -m 0644 %{qemu_kvm_build}/scripts/systemtap/conf.d/qemu_kvm.conf "%{buildroot}%{_datadir}/%{name}/systemtap/conf.d/"


rm %{buildroot}/%{_datadir}/applications/qemu.desktop
rm %{buildroot}%{_bindir}/qemu-system-%{kvm_target}
rm %{buildroot}%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp
rm %{buildroot}%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}-simpletrace.stp
rm %{buildroot}%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}-log.stp

# Install simpletrace
install -m 0755 scripts/simpletrace.py %{buildroot}%{_datadir}/%{name}/simpletrace.py
# Avoid ambiguous 'python' interpreter name
mkdir -p %{buildroot}%{_datadir}/%{name}/tracetool
install -m 0644 -t %{buildroot}%{_datadir}/%{name}/tracetool scripts/tracetool/*.py
mkdir -p %{buildroot}%{_datadir}/%{name}/tracetool/backend
install -m 0644 -t %{buildroot}%{_datadir}/%{name}/tracetool/backend scripts/tracetool/backend/*.py
mkdir -p %{buildroot}%{_datadir}/%{name}/tracetool/format
install -m 0644 -t %{buildroot}%{_datadir}/%{name}/tracetool/format scripts/tracetool/format/*.py

mkdir -p %{buildroot}%{qemudocdir}
install -p -m 0644 -t %{buildroot}%{qemudocdir} README.rst README.systemtap COPYING COPYING.LIB LICENSE

# Rename man page
pushd %{buildroot}%{_mandir}/man1/
for fn in qemu.1*; do
     mv $fn "qemu-kvm${fn#qemu}"
done
popd

install -D -p -m 0644 qemu.sasl %{buildroot}%{_sysconfdir}/sasl2/%{name}.conf

# Provided by package openbios
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-ppc
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-sparc32
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-sparc64
# Provided by package SLOF
rm -rf %{buildroot}%{_datadir}/%{name}/slof.bin

# Remove unpackaged files.
rm -rf %{buildroot}%{_datadir}/%{name}/palcode-clipper
rm -rf %{buildroot}%{_datadir}/%{name}/petalogix*.dtb
rm -f %{buildroot}%{_datadir}/%{name}/bamboo.dtb
rm -f %{buildroot}%{_datadir}/%{name}/ppc_rom.bin
rm -rf %{buildroot}%{_datadir}/%{name}/s390-zipl.rom
rm -rf %{buildroot}%{_datadir}/%{name}/u-boot.e500
rm -rf %{buildroot}%{_datadir}/%{name}/qemu_vga.ndrv
rm -rf %{buildroot}%{_datadir}/%{name}/skiboot.lid
rm -rf %{buildroot}%{_datadir}/%{name}/qboot.rom
rm -rf %{buildroot}%{_datadir}/%{name}/pnv-pnor.bin

rm -rf %{buildroot}%{_datadir}/%{name}/s390-ccw.img
rm -rf %{buildroot}%{_datadir}/%{name}/hppa-firmware.img
rm -rf %{buildroot}%{_datadir}/%{name}/hppa-firmware64.img
rm -rf %{buildroot}%{_datadir}/%{name}/canyonlands.dtb
rm -rf %{buildroot}%{_datadir}/%{name}/u-boot-sam460-20100605.bin

rm -rf %{buildroot}%{_datadir}/%{name}/firmware
rm -rf %{buildroot}%{_datadir}/%{name}/edk2-*.fd
rm -rf %{buildroot}%{_datadir}/%{name}/edk2-licenses.txt

rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv32-sifive_u-fw_jump.bin
rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv32-virt-fw_jump.bin
rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv32-generic-fw_dynamic.*
rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv64-sifive_u-fw_jump.bin
rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv64-virt-fw_jump.bin
rm -rf %{buildroot}%{_datadir}/%{name}/opensbi-riscv64-generic-fw_dynamic.*
rm -rf %{buildroot}%{_datadir}/%{name}/qemu-nsis.bmp
rm -rf %{buildroot}%{_datadir}/%{name}/npcm7xx_bootrom.bin
rm -rf %{buildroot}%{_datadir}/%{name}/npcm8xx_bootrom.bin

# Remove virtfs-proxy-helper files
rm -rf %{buildroot}%{_libexecdir}/virtfs-proxy-helper
rm -rf %{buildroot}%{_mandir}/man1/virtfs-proxy-helper*

%ifarch s390x
    # Use the s390-ccw.img that we've just built, not the pre-built one
    install -m 0644 %{qemu_kvm_build}/pc-bios/s390-ccw/s390-ccw.img %{buildroot}%{_datadir}/%{name}/
    # Remove uefi vars
    rm -rf %{buildroot}%{_libdir}/%{name}/hw-uefi-vars.so
%else
    rm -rf %{buildroot}%{_libdir}/%{name}/hw-s390x-virtio-gpu-ccw.so
%endif

%ifnarch x86_64
    rm -rf %{buildroot}%{_datadir}/%{name}/kvmvapic.bin
    rm -rf %{buildroot}%{_datadir}/%{name}/linuxboot.bin
    rm -rf %{buildroot}%{_datadir}/%{name}/multiboot.bin
    rm -rf %{buildroot}%{_datadir}/%{name}/multiboot_dma.bin
    rm -rf %{buildroot}%{_datadir}/%{name}/pvh.bin
%else
    rm -rf %{buildroot}%{_bindir}/qemu-vmsr-helper
%endif

# Remove sparc files
rm -rf %{buildroot}%{_datadir}/%{name}/QEMU,tcx.bin
rm -rf %{buildroot}%{_datadir}/%{name}/QEMU,cgthree.bin

# Remove ivshmem example programs
rm -rf %{buildroot}%{_bindir}/ivshmem-client
rm -rf %{buildroot}%{_bindir}/ivshmem-server

# Remove efi roms
rm -rf %{buildroot}%{_datadir}/%{name}/efi*.rom

# Provided by package ipxe
rm -rf %{buildroot}%{_datadir}/%{name}/pxe*rom
# Provided by package vgabios
rm -rf %{buildroot}%{_datadir}/%{name}/vgabios*bin
# Provided by package seabios
rm -rf %{buildroot}%{_datadir}/%{name}/bios*.bin

# Remove vof roms
rm -rf %{buildroot}%{_datadir}/%{name}/vof-nvram.bin
rm -rf %{buildroot}%{_datadir}/%{name}/vof.bin

%if %{have_modules_load}
    install -D -p -m 644 %{_sourcedir}/modules-load.conf %{buildroot}%{_sysconfdir}/modules-load.d/kvm.conf
%endif

%if %{have_memlock_limits}
    install -D -p -m 644 %{_sourcedir}/95-kvm-memlock.conf %{buildroot}%{_sysconfdir}/security/limits.d/95-kvm-memlock.conf
%endif

# Install rules to use the bridge helper with libvirt's virbr0
install -D -m 0644 %{_sourcedir}/bridge.conf %{buildroot}%{_sysconfdir}/%{name}/bridge.conf

# Install qemu-pr-helper service
install -m 0644 contrib/systemd/qemu-pr-helper.service %{buildroot}%{_unitdir}
install -m 0644 contrib/systemd/qemu-pr-helper.socket %{buildroot}%{_unitdir}

# We do not support gl display devices so we can remove their modules as they
# do not have expected functionality included.
#
# https://gitlab.com/qemu-project/qemu/-/issues/1352 was filed to stop building these
# modules in case all dependencies are not satisfied.

rm -rf %{buildroot}%{_libdir}/%{name}/hw-display-virtio-gpu-gl.so
rm -rf %{buildroot}%{_libdir}/%{name}/hw-display-virtio-gpu-pci-gl.so
rm -rf %{buildroot}%{_libdir}/%{name}/hw-display-virtio-vga-gl.so

# We need to make the block device modules and other qemu SO files executable
# otherwise RPM won't pick up their dependencies.
chmod +x %{buildroot}%{_libdir}/%{name}/*.so

# Remove docs we don't care about
find %{buildroot}%{qemudocdir} -name .buildinfo -delete
rm -rf %{buildroot}%{qemudocdir}/specs

# endif !tools_only
%endif

%check
%if !%{tools_only}

pushd %{qemu_kvm_build}
echo "Testing %{name}-build"
#%make_build check
make V=1 check
popd

# endif !tools_only
%endif

%post -n qemu-guest-agent
%systemd_post qemu-guest-agent.service
%preun -n qemu-guest-agent
%systemd_preun qemu-guest-agent.service
%postun -n qemu-guest-agent
%systemd_postun_with_restart qemu-guest-agent.service

%if !%{tools_only}
%post common
getent group kvm >/dev/null || groupadd -g 36 -r kvm
getent group qemu >/dev/null || groupadd -g 107 -r qemu
getent passwd qemu >/dev/null || \
useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
  -c "qemu user" qemu

# If this is a new installation, then load kvm modules now, so we can make
# sure that the user gets a system where KVM is ready to use. In case of
# an upgrade, don't try to modprobe again in case the user unloaded the
# kvm module on purpose.
%if %{have_modules_load}
    if [ "$1" = "1" ]; then
        modprobe -b kvm  &> /dev/null || :
    fi
%endif
# endif !tools_only
%endif



%files -n qemu-img
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_bindir}/qemu-storage-daemon
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*
%{_mandir}/man1/qemu-storage-daemon.1*
%{_mandir}/man7/qemu-storage-daemon-qmp-ref.7*


%files -n qemu-guest-agent
%doc COPYING README.rst
%{_bindir}/qemu-ga
%{_mandir}/man8/qemu-ga.8*
%{_unitdir}/qemu-guest-agent.service
%{_udevrulesdir}/99-qemu-guest-agent.rules
%config(noreplace) %{_sysconfdir}/sysconfig/qemu-ga
%{_sysconfdir}/qemu-ga
%{_datadir}/%{name}/qemu-ga
%dir %{_localstatedir}/log/qemu-ga


%if !%{tools_only}
%files
# Deliberately empty

%files tools
%{_bindir}/qemu-keymap
%{_bindir}/qemu-edid
%{_bindir}/qemu-trace-stap
%{_bindir}/elf2dmp
%{_datadir}/%{name}/simpletrace.py*
%{_datadir}/%{name}/tracetool/*.py*
%{_datadir}/%{name}/tracetool/backend/*.py*
%{_datadir}/%{name}/tracetool/format/*.py*
%{_datadir}/%{name}/dump-guest-memory.py*
%{_datadir}/%{name}/trace-events-all
%{_mandir}/man1/qemu-trace-stap.1*

%files -n qemu-pr-helper
%{_bindir}/qemu-pr-helper
%{_unitdir}/qemu-pr-helper.service
%{_unitdir}/qemu-pr-helper.socket
%{_mandir}/man8/qemu-pr-helper.8*

%files docs
%doc %{qemudocdir}

%files common
%license COPYING COPYING.LIB LICENSE
%{_mandir}/man7/qemu-qmp-ref.7*
%{_mandir}/man7/qemu-cpu-models.7*
%{_mandir}/man7/qemu-ga-ref.7*

%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/keymaps/
%{_mandir}/man1/%{name}.1*
%{_mandir}/man7/qemu-block-drivers.7*
%attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
%config(noreplace) %{_sysconfdir}/sasl2/%{name}.conf
%ghost %{_sysconfdir}/kvm
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/bridge.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/vhost.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/kvm.conf

%ifarch x86_64
    %{_datadir}/%{name}/linuxboot.bin
    %{_datadir}/%{name}/multiboot.bin
    %{_datadir}/%{name}/multiboot_dma.bin
    %{_datadir}/%{name}/kvmvapic.bin
    %{_datadir}/%{name}/pvh.bin
%endif
%ifarch s390x
    %{_datadir}/%{name}/s390-ccw.img
%else
    %{_libdir}/%{name}/hw-uefi-vars.so
%endif
%{_datadir}/icons/*
%{_datadir}/%{name}/linuxboot_dma.bin
%if %{have_modules_load}
    %{_sysconfdir}/modules-load.d/kvm.conf
%endif
%if %{have_memlock_limits}
    %{_sysconfdir}/security/limits.d/95-kvm-memlock.conf
%endif

%files core
%{_libexecdir}/qemu-kvm
%{_datadir}/systemtap/tapset/qemu-kvm.stp
%{_datadir}/systemtap/tapset/qemu-kvm-log.stp
%{_datadir}/systemtap/tapset/qemu-kvm-simpletrace.stp
%{_datadir}/%{name}/systemtap/script.d/qemu_kvm.stp
%{_datadir}/%{name}/systemtap/conf.d/qemu_kvm.conf
%{_datadir}/systemtap/tapset/qemu-img*.stp
%{_datadir}/systemtap/tapset/qemu-io*.stp
%{_datadir}/systemtap/tapset/qemu-nbd*.stp
%{_datadir}/systemtap/tapset/qemu-storage-daemon*.stp

%files device-display-virtio-gpu
%{_libdir}/%{name}/hw-display-virtio-gpu.so

%ifarch s390x
%files device-display-virtio-gpu-ccw
    %{_libdir}/%{name}/hw-s390x-virtio-gpu-ccw.so
%else
%files device-display-virtio-gpu-pci
    %{_libdir}/%{name}/hw-display-virtio-gpu-pci.so
%endif

%ifarch x86_64 %{power64}
%files device-display-virtio-vga
    %{_libdir}/%{name}/hw-display-virtio-vga.so
%endif

%files tests
%{testsdir}
%{_libdir}/%{name}/accel-qtest-%{kvm_target}.so

%files block-blkio
%{_libdir}/%{name}/block-blkio.so

%files block-curl
%{_libdir}/%{name}/block-curl.so
%if %{have_block_rbd}
%files block-rbd
%{_libdir}/%{name}/block-rbd.so
%endif
%files audio-pa
%{_libdir}/%{name}/audio-pa.so

%if %{have_opengl}
%files ui-opengl
%{_libdir}/%{name}/ui-opengl.so
%files ui-egl-headless
%{_libdir}/%{name}/ui-egl-headless.so
%endif

%files device-usb-host
%{_libdir}/%{name}/hw-usb-host.so

%if %{have_usbredir}
%files device-usb-redirect
    %{_libdir}/%{name}/hw-usb-redirect.so
%endif

%files audio-dbus
%{_libdir}/%{name}/audio-dbus.so

%files ui-dbus
%{_libdir}/%{name}/ui-dbus.so

# endif !tools_only
%endif

%changelog
* Wed Sep 17 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-14
- kvm-hw-uefi-clear-uefi-vars-buffer-in-uefi_vars_write-ca.patch [RHEL-108614]
- kvm-hw-uefi-return-success-for-notifications.patch [RHEL-108614]
- kvm-hw-uefi-check-access-for-first-variable.patch [RHEL-108614]
- Resolves: RHEL-108614
  (CVE-2025-8860 qemu-kvm: uefi-vars: information disclosure vulnerability in uefi_vars_write callback [rhel-10.1])

* Wed Sep 10 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-13
- Added TDX support
- Resolves: RHEL-20797
  ([Intel 10.0 FEAT] TDX: host: Virt-QEMU: Add safe device pass-through for TD)
- Resolves: RHEL-49727
  ([Intel 10.0 FEAT] [SPR][EMR] Virt-QEMU: TDX: Allow to configure apic bus clock)
- Resolves: RHEL-50307
  ([Intel 10.0 FEAT] [SPR] TDX: Virt-QEMU: QEMU Support)

* Thu Aug 21 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-12
- kvm-RHEL-Pack-uefi-vars-module.patch [RHEL-102325]
- Resolves: RHEL-102325
  ([qemu] enable variable service for edk2)

* Mon Aug 18 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-11
- kvm-rbd-Fix-.bdrv_get_specific_info-implementation.patch [RHEL-105440]
- Resolves: RHEL-105440
  (Openstack guest becomes inaccessible via network when storage network on the hypervisor is disabled/lost [rhel-10.1])

* Tue Aug 12 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-10
- kvm-Enable-uefi-variable-service-for-edk2.patch [RHEL-102325]
- Resolves: RHEL-102325
  ([qemu] enable variable service for edk2)

* Mon Aug 04 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-9
- kvm-Declare-rtl8139-as-deprecated.patch [RHEL-45624]
- Resolves: RHEL-45624
  (Deprecate rtl8139 NIC in QEMU)

* Mon Jul 28 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-8
- kvm-migration-multifd-move-macros-to-multifd-header.patch [RHEL-59697]
- kvm-migration-refactor-channel-discovery-mechanism.patch [RHEL-59697]
- kvm-migration-Add-save_postcopy_prepare-savevm-handler.patch [RHEL-59697]
- kvm-migration-ram-Implement-save_postcopy_prepare.patch [RHEL-59697]
- kvm-tests-qtest-migration-consolidate-set-capabilities.patch [RHEL-59697]
- kvm-migration-write-zero-pages-when-postcopy-enabled.patch [RHEL-59697]
- kvm-migration-enable-multifd-and-postcopy-together.patch [RHEL-59697]
- kvm-migration-Add-qtest-for-migration-over-RDMA.patch [RHEL-59697]
- kvm-qtest-migration-rdma-Enforce-RLIMIT_MEMLOCK-128MB-re.patch [RHEL-59697]
- kvm-qtest-migration-rdma-Add-test-for-rdma-migration-wit.patch [RHEL-59697]
- kvm-tests-qtest-migration-add-postcopy-tests-with-multif.patch [RHEL-59697]
- kvm-file-posix-Fix-aio-threads-performance-regression-af.patch [RHEL-96854]
- kvm-block-remove-outdated-comments-about-AioContext-lock.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-read-locked-bdrv_reopen_.patch [RHEL-88561]
- kvm-block-snapshot-move-drain-outside-of-read-locked-bdr.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-read-locked-bdrv_inactiv.patch [RHEL-88561]
- kvm-block-mark-bdrv_parent_change_aio_context-GRAPH_RDLO.patch [RHEL-88561]
- kvm-block-mark-change_aio_ctx-callback-and-instances-as-.patch [RHEL-88561]
- kvm-block-mark-bdrv_child_change_aio_context-GRAPH_RDLOC.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_change_aio_context-.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_try_change_aio_cont.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_attach_child_common.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_set_backing_hd_drai.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_root_attach_child.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_attach_child.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-quorum_add_child.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-bdrv_root_unref_child.patch [RHEL-88561]
- kvm-block-move-drain-outside-of-quorum_del_child.patch [RHEL-88561]
- kvm-blockdev-drain-while-unlocked-in-internal_snapshot_a.patch [RHEL-88561]
- kvm-blockdev-drain-while-unlocked-in-external_snapshot_a.patch [RHEL-88561]
- kvm-block-mark-bdrv_drained_begin-and-friends-as-GRAPH_U.patch [RHEL-88561]
- kvm-iotests-graph-changes-while-io-remove-image-file-aft.patch [RHEL-88561]
- kvm-iotests-graph-changes-while-io-add-test-case-with-re.patch [RHEL-88561]
- Resolves: RHEL-59697
  (Allow multifd+postcopy features being enabled together, but only use multifd during precopy )
- Resolves: RHEL-96854
  (Performance Degradation(aio=threads) between Upstream Commit b75c5f9 and 984a32f)
- Resolves: RHEL-88561
  (qemu graph deadlock during job-dismiss)

* Mon Jul 07 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-7
- kvm-s390x-Fix-leak-in-machine_set_loadparm.patch [RHEL-98555]
- kvm-hw-s390x-ccw-device-Fix-memory-leak-in-loadparm-sett.patch [RHEL-98555]
- kvm-target-i386-Update-EPYC-CPU-model-for-Cache-property.patch [RHEL-52650]
- kvm-target-i386-Update-EPYC-Rome-CPU-model-for-Cache-pro.patch [RHEL-52650]
- kvm-target-i386-Update-EPYC-Milan-CPU-model-for-Cache-pr.patch [RHEL-52650]
- kvm-target-i386-Add-couple-of-feature-bits-in-CPUID_Fn80.patch [RHEL-52650]
- kvm-target-i386-Update-EPYC-Genoa-for-Cache-property-per.patch [RHEL-52650]
- kvm-target-i386-Add-support-for-EPYC-Turin-model.patch [RHEL-52650]
- kvm-include-qemu-compiler-add-QEMU_UNINITIALIZED-attribu.patch [RHEL-95479]
- kvm-hw-virtio-virtio-avoid-cost-of-ftrivial-auto-var-ini.patch [RHEL-95479]
- kvm-block-skip-automatic-zero-init-of-large-array-in-ioq.patch [RHEL-95479]
- kvm-chardev-char-fd-skip-automatic-zero-init-of-large-ar.patch [RHEL-95479]
- kvm-chardev-char-pty-skip-automatic-zero-init-of-large-a.patch [RHEL-95479]
- kvm-chardev-char-socket-skip-automatic-zero-init-of-larg.patch [RHEL-95479]
- kvm-hw-audio-ac97-skip-automatic-zero-init-of-large-arra.patch [RHEL-95479]
- kvm-hw-audio-cs4231a-skip-automatic-zero-init-of-large-a.patch [RHEL-95479]
- kvm-hw-audio-es1370-skip-automatic-zero-init-of-large-ar.patch [RHEL-95479]
- kvm-hw-audio-gus-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-hw-audio-marvell_88w8618-skip-automatic-zero-init-of.patch [RHEL-95479]
- kvm-hw-audio-sb16-skip-automatic-zero-init-of-large-arra.patch [RHEL-95479]
- kvm-hw-audio-via-ac97-skip-automatic-zero-init-of-large-.patch [RHEL-95479]
- kvm-hw-char-sclpconsole-lm-skip-automatic-zero-init-of-l.patch [RHEL-95479]
- kvm-hw-dma-xlnx_csu_dma-skip-automatic-zero-init-of-larg.patch [RHEL-95479]
- kvm-hw-display-vmware_vga-skip-automatic-zero-init-of-la.patch [RHEL-95479]
- kvm-hw-hyperv-syndbg-skip-automatic-zero-init-of-large-a.patch [RHEL-95479]
- kvm-hw-misc-aspeed_hace-skip-automatic-zero-init-of-larg.patch [RHEL-95479]
- kvm-hw-net-rtl8139-skip-automatic-zero-init-of-large-arr.patch [RHEL-95479]
- kvm-hw-net-tulip-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-hw-net-virtio-net-skip-automatic-zero-init-of-large-.patch [RHEL-95479]
- kvm-hw-net-xgamc-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-hw-nvme-ctrl-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-hw-ppc-pnv_occ-skip-automatic-zero-init-of-large-str.patch [RHEL-95479]
- kvm-hw-ppc-spapr_tpm_proxy-skip-automatic-zero-init-of-l.patch [RHEL-95479]
- kvm-hw-usb-hcd-ohci-skip-automatic-zero-init-of-large-ar.patch [RHEL-95479]
- kvm-hw-scsi-lsi53c895a-skip-automatic-zero-init-of-large.patch [RHEL-95479]
- kvm-hw-scsi-megasas-skip-automatic-zero-init-of-large-ar.patch [RHEL-95479]
- kvm-hw-ufs-lu-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-net-socket-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-net-stream-skip-automatic-zero-init-of-large-array.patch [RHEL-95479]
- kvm-hw-i386-amd_iommu-Isolate-AMDVI-PCI-from-amd-iommu-d.patch [RHEL-85649]
- kvm-hw-i386-amd_iommu-Allow-migration-when-explicitly-cr.patch [RHEL-85649]
- kvm-Enable-amd-iommu-device.patch [RHEL-85649]
- kvm-ui-vnc-Update-display-update-interval-when-VM-state-.patch [RHEL-83883]
- Resolves: RHEL-98555
  ([s390x][RHEL10.1][ccw-device] there would be memory leak with virtio_blk disks)
- Resolves: RHEL-52650
  ([AMDSERVER 10.1 Feature] Turin: Qemu EPYC-Turin Model)
- Resolves: RHEL-95479
  (-ftrivial-auto-var-init=zero reduced performance)
- Resolves: RHEL-85649
  ([RHEL 10]Qemu/amd-iommu: Add ability to manually specify the AMDVI-PCI device)
- Resolves: RHEL-83883
  (Video stuck after switchover phase when play one video during migration)

* Fri Jun 20 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-6
- kvm-scsi-disk-Add-native-FUA-write-support.patch [RHEL-71962]
- kvm-Fix-handling-of-have_block_rbd.patch [RHEL-96057]
- kvm-Delete-obsolete-references-to-architectures.patch [RHEL-96057]
- kvm-Fix-arch-list-for-vgabios-and-ipxe-roms.patch [RHEL-96057]
- kvm-Disable-virtio-net-pci-romfile-loading-on-riscv64.patch [RHEL-96057]
- Resolves: RHEL-71962
  ([RFE] Implement FUA support in scsi-disk)
- Resolves: RHEL-96057
  (qemu-kvm: Various small issues in the spec file)

* Mon Jun 09 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-5
- kvm-file-posix-Define-DM_MPATH_PROBE_PATHS.patch [RHEL-65852]
- kvm-file-posix-Probe-paths-and-retry-SG_IO-on-potential-.patch [RHEL-65852]
- kvm-io-Fix-partial-struct-copy-in-qio_dns_resolver_looku.patch [RHEL-67706]
- kvm-util-qemu-sockets-Refactor-setting-client-sockopts-i.patch [RHEL-67706]
- kvm-util-qemu-sockets-Refactor-success-and-failure-paths.patch [RHEL-67706]
- kvm-util-qemu-sockets-Add-support-for-keep-alive-flag-to.patch [RHEL-67706]
- kvm-util-qemu-sockets-Refactor-inet_parse-to-use-QemuOpt.patch [RHEL-67706]
- kvm-util-qemu-sockets-Introduce-inet-socket-options-cont.patch [RHEL-67706]
- kvm-tests-unit-test-util-sockets-fix-mem-leak-on-error-o.patch [RHEL-67706]
- Resolves: RHEL-65852
  (Support multipath failover with scsi-block)
- Resolves: RHEL-67706
  (postcopy on the destination host can't switch into pause status under the network issue if boot VM with '-S')

* Mon May 26 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-4
- kvm-block-Expand-block-status-mode-from-bool-to-flags.patch [RHEL-88435 RHEL-88437]
- kvm-file-posix-gluster-Handle-zero-block-status-hint-bet.patch [RHEL-88435 RHEL-88437]
- kvm-block-Let-bdrv_co_is_zero_fast-consolidate-adjacent-.patch [RHEL-88435 RHEL-88437]
- kvm-block-Add-new-bdrv_co_is_all_zeroes-function.patch [RHEL-88435 RHEL-88437]
- kvm-iotests-Improve-iotest-194-to-mirror-data.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Minor-refactoring.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Pass-full-sync-mode-rather-than-bool-to-inter.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Allow-QMP-override-to-declare-target-already-.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Drop-redundant-zero_target-parameter.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Skip-pre-zeroing-destination-if-it-is-already.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Skip-writing-zeroes-when-target-is-already-ze.patch [RHEL-88435 RHEL-88437]
- kvm-iotests-common.rc-add-disk_usage-function.patch [RHEL-88435 RHEL-88437]
- kvm-tests-Add-iotest-mirror-sparse-for-recent-patches.patch [RHEL-88435 RHEL-88437]
- kvm-mirror-Reduce-I-O-when-destination-is-detect-zeroes-.patch [RHEL-88435 RHEL-88437]
- Resolves: RHEL-88435
  (--migrate-disks-detect-zeroes doesn't take effect for disk migration [rhel-10.1])
- Resolves: RHEL-88437
  (Disk size of target raw image is full allocated when doing mirror with default discard value [rhel-10.1])

* Mon May 19 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-3
- kvm-migration-postcopy-Spatial-locality-page-hint-for-pr.patch [RHEL-85635]
- kvm-meson-configure-add-valgrind-option-en-dis-able-valg.patch [RHEL-88457]
- kvm-distro-add-an-explicit-valgrind-devel-build-dep.patch [RHEL-88457]
- kvm-Allow-guest-get-load-QGA-command.patch [RHEL-91219]
- Resolves: RHEL-85635
  (Video stuck about 1 min after switchover phase when play one video during postcopy-preempt migration)
- Resolves: RHEL-88457
  (qemu inadvertantly built with valgrind coroutine stack debugging on x86_64)
- Resolves: RHEL-91219
  ([qemu-guest-agent] Enable 'guest-get-load' by default [RHEL-10])

* Mon May 12 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-2
- kvm-file-posix-probe-discard-alignment-on-Linux-block-de.patch [RHEL-87642]
- kvm-block-io-skip-head-tail-requests-on-EINVAL.patch [RHEL-87642]
- kvm-file-posix-Fix-crash-on-discard_granularity-0.patch [RHEL-87642]
- kvm-Enable-vhost-user-gpu-pci-for-RHIVOS.patch [RHEL-86056]
- Resolves: RHEL-87642
  (QEMU sends unaligned discards on 4K devices[RHEL-10])
- Resolves: RHEL-86056
  (Enable 'vhost-user-gpu-pci' in qemu-kvm for RHIVOS)

* Wed Apr 23 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.0.0-1
- Rebase to QEMU 10.0.0 [RHEL-74473]
- Resolves: RHEL-74473
  (Rebase qemu-kvm to QEMU 10.0.0)

* Mon Apr 07 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-17
- kvm-Also-recommend-systemtap-devel-from-qemu-tools.patch [RHEL-83535]
- Resolves: RHEL-83535
  ([Qemu RHEL-10] qemu-trace-stap should handle lack of stap more gracefully)

* Tue Mar 25 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-16
- kvm-migration-Fix-UAF-for-incoming-migration-on-Migratio.patch [RHEL-69776]
- kvm-scripts-improve-error-from-qemu-trace-stap-on-missin.patch [RHEL-83535]
- kvm-Recommend-systemtap-client-from-qemu-tools.patch [RHEL-83535]
- Resolves: RHEL-69776
  ([rhel10]Guest crashed on the target host when the migration was canceled)
- Resolves: RHEL-83535
  ([Qemu RHEL-10] qemu-trace-stap should handle lack of stap more gracefully)

* Mon Feb 17 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-15
- kvm-migration-Add-helper-to-get-target-runstate.patch [RHEL-54670]
- kvm-qmp-cont-Only-activate-disks-if-migration-completed.patch [RHEL-54670]
- kvm-migration-block-Make-late-block-active-the-default.patch [RHEL-54670]
- kvm-migration-block-Apply-late-block-active-behavior-to-.patch [RHEL-54670]
- kvm-migration-block-Fix-possible-race-with-block_inactiv.patch [RHEL-54670]
- kvm-migration-block-Rewrite-disk-activation.patch [RHEL-54670]
- kvm-block-Add-active-field-to-BlockDeviceInfo.patch [RHEL-54670]
- kvm-block-Allow-inactivating-already-inactive-nodes.patch [RHEL-54670]
- kvm-block-Inactivate-external-snapshot-overlays-when-nec.patch [RHEL-54670]
- kvm-migration-block-active-Remove-global-active-flag.patch [RHEL-54670]
- kvm-block-Don-t-attach-inactive-child-to-active-node.patch [RHEL-54670]
- kvm-block-Fix-crash-on-block_resize-on-inactive-node.patch [RHEL-54670]
- kvm-block-Add-option-to-create-inactive-nodes.patch [RHEL-54670]
- kvm-block-Add-blockdev-set-active-QMP-command.patch [RHEL-54670]
- kvm-block-Support-inactive-nodes-in-blk_insert_bs.patch [RHEL-54670]
- kvm-block-export-Don-t-ignore-image-activation-error-in-.patch [RHEL-54670]
- kvm-block-Drain-nodes-before-inactivating-them.patch [RHEL-54670]
- kvm-block-export-Add-option-to-allow-export-of-inactive-.patch [RHEL-54670]
- kvm-nbd-server-Support-inactive-nodes.patch [RHEL-54670]
- kvm-iotests-Add-filter_qtest.patch [RHEL-54670]
- kvm-iotests-Add-qsd-migrate-case.patch [RHEL-54670]
- kvm-iotests-Add-NBD-based-tests-for-inactive-nodes.patch [RHEL-54670]
- Resolves: RHEL-54670
  (Provide QMP command for block device reactivation after migration [rhel-10.0])

* Mon Feb 10 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-14
- kvm-net-Fix-announce_self.patch [RHEL-73894]
- kvm-vhost-Add-stubs-for-the-migration-state-transfer-int.patch [RHEL-78370]
- kvm-virtio-net-vhost-user-Implement-internal-migration.patch [RHEL-78370]
- Resolves: RHEL-73894
  (No RARP packets on the destination after migration [rhel-10])
- Resolves: RHEL-78370
  (Add vhost-user internal migration for passt)

* Mon Feb 03 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-13
- kvm-nbd-server-Silence-server-warnings-on-port-probes.patch [RHEL-76908]
- Resolves: RHEL-76908
  (Ensure qemu as NBD server does not flood logs [rhel-10])

* Mon Jan 27 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-12
- kvm-pci-ensure-valid-link-status-bits-for-downstream-por.patch [RHEL-65618]
- kvm-pc-bios-s390-ccw-Abort-IPL-on-invalid-loadparm.patch [RHEL-72717]
- kvm-pc-bios-s390-ccw-virtio-Add-a-function-to-reset-a-vi.patch [RHEL-72717]
- kvm-pc-bios-s390-ccw-Fix-boot-problem-with-virtio-net-de.patch [RHEL-72717]
- kvm-pc-bios-s390-ccw-netmain-Fix-error-messages-with-reg.patch [RHEL-72717]
- kvm-arm-disable-pauth-for-virt-rhel9-in-RHEL10.patch [RHEL-71761]
- Resolves: RHEL-65618
  ([RHEL10] Failed to hot add PCIe device behind xio3130 downstream)
- Resolves: RHEL-72717
  (Boot fall back to cdrom from network not always working)
- Resolves: RHEL-71761
  ([Nvidia "Grace"] Lack of "PAuth" CPU feature results in live migration failure from RHEL 9.6 to 10)

* Mon Jan 20 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-11
- kvm-target-i386-Make-sure-SynIC-state-is-really-updated-.patch [RHEL-73002]
- kvm-hw-virtio-fix-crash-in-processing-balloon-stats.patch [RHEL-73835]
- kvm-qga-Add-log-to-guest-fsfreeze-thaw-command.patch [RHEL-74361]
- kvm-qemu-ga-Optimize-freeze-hook-script-logic-of-logging.patch [RHEL-74461]
- Resolves: RHEL-73002
  (kvm-unti kvm-hyperv_synic test is stuck on AMD with COS9 [rhel-10])
- Resolves: RHEL-73835
  (VM crashes when requesting domstats [rhel-10])
- Resolves: RHEL-74361
  (qemu-ga logs only "guest-fsfreeze called" (but not "guest-fsthaw called"))
- Resolves: RHEL-74461
  (fsfreeze hooks doesn't log error on system logs when running hook fails [rhel-10])

* Mon Jan 13 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-10
- kvm-qdev-Fix-set_pci_devfn-to-visit-option-only-once.patch [RHEL-43412]
- kvm-tests-avocado-hotplug_blk-Fix-addr-in-device_add-com.patch [RHEL-43412]
- kvm-qdev-monitor-avoid-QemuOpts-in-QMP-device_add.patch [RHEL-43412]
- kvm-vl-use-qmp_device_add-in-qemu_create_cli_devices.patch [RHEL-43412]
- kvm-pc-q35-Bump-max_cpus-to-4096-vcpus.patch [RHEL-57668]
- kvm-vhost-fail-device-start-if-iotlb-update-fails.patch [RHEL-73005]
- kvm-virtio-net-disable-USO-for-all-RHEL9.patch [RHEL-69500]
- Resolves: RHEL-43412
  (qom-get iothread-vq-mapping is empty on new hotplug disk [rhel-10.0-beta])
- Resolves: RHEL-57668
  ([RFE] [HPEMC] [RHEL-10.0] qemu-kvm: support up to 4096 VCPUs)
- Resolves: RHEL-73005
  (qemu-kvm: vhost: reports error while updating IOTLB entries)
- Resolves: RHEL-69500
  ([Stable_Guest_ABI][USO][9.6.0-machine-type]From 10.0 to RHEL.9.6.0 the guest with 9.6 machine type only, the guest crashed with - qemu-kvm: Features 0x1c0010130afffa7 unsupported. Allowed features: 0x10179bfffe7)

* Mon Jan 06 2025 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-9
- kvm-linux-headers-Update-to-Linux-v6.12-rc5.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-msa10-subfunctions.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-msa11-subfunctions.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-msa12-changes.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-msa13-subfunctions.patch [RHEL-32665]
- kvm-s390x-cpumodel-Add-ptff-Query-Time-Stamp-Event-QTSE-.patch [RHEL-32665]
- kvm-linux-headers-Update-to-Linux-6.13-rc1.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-Concurrent-functions-facility-sup.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-Vector-Enhancements-facility-3.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-Miscellaneous-Instruction-Extensi.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-Vector-Packed-Decimal-Enhancement.patch [RHEL-32665]
- kvm-s390x-cpumodel-add-Ineffective-nonconstrained-transa.patch [RHEL-32665]
- kvm-s390x-cpumodel-Add-Sequential-Instruction-Fetching-f.patch [RHEL-32665]
- kvm-s390x-cpumodel-correct-PLO-feature-wording.patch [RHEL-32665]
- kvm-s390x-cpumodel-Add-PLO-extension-facility.patch [RHEL-32665]
- kvm-s390x-cpumodel-gen17-model.patch [RHEL-32665]
- kvm-qga-skip-bind-mounts-in-fs-list.patch [RHEL-71939]
- kvm-hw-char-pl011-Use-correct-masks-for-IBRD-and-FBRD.patch [RHEL-67108]
- Resolves: RHEL-32665
  ([IBM 10.0 FEAT] KVM: CPU model for new IBM Z HW - qemu-kvm part)
- Resolves: RHEL-71939
  (qemu-ga cannot freeze filesystems with sentinelone)
- Resolves: RHEL-67108
  ([aarch64] [rhel-10.0] Backport some important post 9.1 qemu fixes)

* Fri Dec 13 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-8
- kvm-migration-Allow-pipes-to-keep-working-for-fd-migrati.patch [RHEL-69047]
- Resolves: RHEL-69047
  (warning: fd: migration to a file is deprecated when create or revert a snapshot)

* Tue Dec 03 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-7
- kvm-virtio-net-Add-queues-before-loading-them.patch [RHEL-58316]
- kvm-docs-system-s390x-bootdevices-Update-loadparm-docume.patch [RHEL-68444]
- kvm-docs-system-bootindex-Make-it-clear-that-s390x-can-a.patch [RHEL-68444]
- kvm-hw-s390x-Restrict-loadparm-property-to-devices-that-.patch [RHEL-68444]
- kvm-hw-Add-loadparm-property-to-scsi-disk-devices-for-bo.patch [RHEL-68444]
- kvm-scsi-fix-allocation-for-s390x-loadparm.patch [RHEL-68444]
- kvm-pc-bios-s390x-Initialize-cdrom-type-to-false-for-eac.patch [RHEL-68444]
- kvm-pc-bios-s390x-Initialize-machine-loadparm-before-pro.patch [RHEL-68444]
- kvm-pc-bios-s390-ccw-Re-initialize-receive-queue-index-b.patch [RHEL-68444]
- Resolves: RHEL-58316
  (qemu crashed when migrate vm with multiqueue from rhel9.4 to rhel10.0)
- Resolves: RHEL-68444
  (The new "boot order" feature is sometimes not working as expected [RHEL 10])

* Mon Nov 25 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-6
- kvm-vfio-container-Fix-container-object-destruction.patch [RHEL-67936]
- kvm-virtio-net-disable-USO-for-RHEL9.patch [RHEL-40950]
- kvm-qemu-guest-agent-add-new-api-to-allow-rpc.patch [RHEL-60223]
- Resolves: RHEL-67936
  (QEMU should fail gracefully with passthrough devices in SEV-SNP guests)
- Resolves: RHEL-40950
  ([Stable_Guest_ABI][USO]From 10-beta to RHEL.9.5.0  the guest with 9.4 machine type only, the guest crashed  with - qemu-kvm: Features 0x1c0010130afffa7 unsupported. Allowed features: 0x10179bfffe7 )
- Resolves: RHEL-60223
  ([qemu-guest-agent] Add new api 'guest-network-get-route' to allow-rpc)

* Tue Nov 19 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-5
- kvm-migration-Ensure-vmstate_save-sets-errp.patch [RHEL-63051]
- kvm-kvm-replace-fprintf-with-error_report-printf-in-kvm_.patch [RHEL-57685]
- kvm-kvm-refactor-core-virtual-machine-creation-into-its-.patch [RHEL-57685]
- kvm-accel-kvm-refactor-dirty-ring-setup.patch [RHEL-57685]
- kvm-KVM-Dynamic-sized-kvm-memslots-array.patch [RHEL-57685]
- kvm-KVM-Define-KVM_MEMSLOTS_NUM_MAX_DEFAULT.patch [RHEL-57685]
- kvm-KVM-Rename-KVMMemoryListener.nr_used_slots-to-nr_slo.patch [RHEL-57685]
- kvm-KVM-Rename-KVMState-nr_slots-to-nr_slots_max.patch [RHEL-57685]
- kvm-Require-new-dtrace-package.patch [RHEL-67899]
- Resolves: RHEL-63051
  (qemu crashed after killed virtiofsd during migration)
- Resolves: RHEL-57685
  (Bad migration performance when performing vGPU VM live migration )
- Resolves: RHEL-67899
  (Failed to build qemu-kvm due to missing dtrace [rhel-10.0])

* Tue Nov 12 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-4.el10
- kvm-accel-kvm-check-for-KVM_CAP_READONLY_MEM-on-VM.patch [RHEL-58928]
- kvm-hw-s390x-ipl-Provide-more-memory-to-the-s390-ccw.img.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Use-the-libc-from-SLOF-and-remove-s.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Link-the-netboot-code-into-the-main.patch [RHEL-58153]
- kvm-redhat-Remove-the-s390-netboot.img-from-the-spec-fil.patch [RHEL-58153]
- kvm-hw-s390x-Remove-the-possibility-to-load-the-s390-net.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Merge-netboot.mak-into-the-main-Mak.patch [RHEL-58153]
- kvm-docs-system-s390x-bootdevices-Update-the-documentati.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Remove-panics-from-ISO-IPL-path.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Remove-panics-from-ECKD-IPL-path.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Remove-panics-from-SCSI-IPL-path.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Remove-panics-from-DASD-IPL-path.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Remove-panics-from-Netboot-IPL-path.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Enable-failed-IPL-to-return-after-e.patch [RHEL-58153]
- kvm-include-hw-s390x-Add-include-files-for-common-IPL-st.patch [RHEL-58153]
- kvm-s390x-Add-individual-loadparm-assignment-to-CCW-devi.patch [RHEL-58153]
- kvm-hw-s390x-Build-an-IPLB-for-each-boot-device.patch [RHEL-58153]
- kvm-s390x-Rebuild-IPLB-for-SCSI-device-directly-from-DIA.patch [RHEL-58153]
- kvm-pc-bios-s390x-Enable-multi-device-boot-loop.patch [RHEL-58153]
- kvm-docs-system-Update-documentation-for-s390x-IPL.patch [RHEL-58153]
- kvm-tests-qtest-Add-s390x-boot-order-tests-to-cdrom-test.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Clarify-alignment-is-in-bytes.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Don-t-generate-TEXTRELs.patch [RHEL-58153]
- kvm-pc-bios-s390-ccw-Introduce-EXTRA_LDFLAGS.patch [RHEL-58153]
- kvm-vnc-fix-crash-when-no-console-attached.patch [RHEL-50529]
- kvm-vfio-migration-Report-only-stop-copy-size-in-vfio_st.patch [RHEL-64308]
- kvm-vfio-migration-Change-trace-formats-from-hex-to-deci.patch [RHEL-64308]
- kvm-kvm-Allow-kvm_arch_get-put_registers-to-accept-Error.patch [RHEL-20574]
- kvm-target-i386-kvm-Report-which-action-failed-in-kvm_ar.patch [RHEL-20574]
- kvm-target-i386-cpu-set-correct-supported-XCR0-features-.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-do-not-rely-on-ExtSaveArea-for-accelerat.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-return-bool-from-x86_cpu_filter_features.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-add-AVX10-feature-and-AVX10-version-prop.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-add-CPUID.24-features-for-AVX10.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-Add-feature-dependencies-for-AVX10.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-Add-AVX512-state-when-AVX10-is-supported.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-Introduce-GraniteRapids-v2-model.patch [RHEL-30315 RHEL-45110]
- kvm-target-i386-add-sha512-sm3-sm4-feature-bits.patch [RHEL-30315 RHEL-45110]
- Resolves: RHEL-58928
  (Boot SNP guests failed with qemu-kvm: kvm_set_user_memory_region)
- Resolves: RHEL-58153
  ([IBM 10.0 FEAT] KVM: Full boot order support - qemu part)
- Resolves: RHEL-50529
  (Qemu-kvm  crashed  if  no display device setting and switching display by remote-viewer)
- Resolves: RHEL-64308
  (High threshold value observed in vGPU live migration)
- Resolves: RHEL-20574
  (Fail migration properly when put cpu register fails)
- Resolves: RHEL-30315
  ([Intel 10.0 FEAT] [GNR] Virt-QEMU: Add AVX10.1 instruction support)
- Resolves: RHEL-45110
  ([Intel 10.0 FEAT] [CWF][DMR] Virt-QEMU: Advertise new instructions SHA2-512NI, SM3, and SM4)

* Tue Oct 29 2024 Troy Dawson <tdawson@redhat.com> - 18:9.1.0-3.1
- Bump release for October 2024 mass rebuild:
  Resolves: RHEL-64018

* Mon Oct 07 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-3
- kvm-hostmem-Apply-merge-property-after-the-memory-region.patch [RHEL-58936]
- Resolves: RHEL-58936
  ([RHEL-10.0] QEMU core dump on applying merge property to memory backend)

* Mon Sep 30 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-2
- kvm-x86-create-new-pc-q35-machine-type-for-rhel-9.6.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-arm-create-new-virt-machine-type-for-rhel-9.6.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-x86-create-pc-i440fx-machine-type-for-rhel10.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-x86-create-pc-q35-machine-type-for-rhel10.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-arm-create-virt-machine-type-for-rhel10.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-x86-remove-deprecated-rhel-machine-types.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-remove-stale-compat-definitions.patch [RHEL-29002 RHEL-29003 RHEL-35587 RHEL-38411 RHEL-45141]
- kvm-RH-Author-Shaoqin-Huang-shahuang-redhat.com.patch [RHEL-38374]
- kvm-qemu-guest-agent-Update-the-logfile-path-of-qga-fsfr.patch [RHEL-57028]
- Resolves: RHEL-29002
  (Remove the existing deprecated machine types in RHEL-10)
- Resolves: RHEL-29003
  (Deprecate RHEL-9 machine types in RHEL-10)
- Resolves: RHEL-35587
  (Create a pc-i440fx-rhel10.0 machine type)
- Resolves: RHEL-38411
  ([Fujitsu 10.0 FEAT]: qemu-kvm: Continue to support i440fx for RHEL10)
- Resolves: RHEL-45141
  (Introduce virt-rhel10.0 arm-virt machine type [aarch64])
- Resolves: RHEL-38374
  (aarch64 SMBIOS 'Manufacturer' and 'Product Name' differ from x86 ones [rhel-10])
- Resolves: RHEL-57028
  (fsfreeze hooks break on the systems first restorecon [rhel-10])

* Tue Sep 10 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.1.0-1
- Rebase to QEMU 9.1.0 [RHEL-41246]
- Resolves: RHEL-41246
  (Rebase qemu-9.1 for RHEL 10.0)

* Mon Aug 26 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-8
- kvm-x86-cpu-update-deprecation-string-to-match-lowest-un.patch [RHEL-54260]
- Resolves: RHEL-54260
  ([RHEL10] Need to update the deprecated CPU model warning message)

* Thu Aug 15 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-7
- kvm-linux-aio-add-IO_CMD_FDSYNC-command-support.patch [RHEL-51901]
- kvm-nbd-server-Plumb-in-new-args-to-nbd_client_add.patch [RHEL-52599]
- kvm-nbd-server-CVE-2024-7409-Cap-default-max-connections.patch [RHEL-52599]
- kvm-nbd-server-CVE-2024-7409-Drop-non-negotiating-client.patch [RHEL-52599]
- kvm-nbd-server-CVE-2024-7409-Close-stray-clients-at-serv.patch [RHEL-52599]
- Resolves: RHEL-51901
  (qemu-kvm: linux-aio: add support for IO_CMD_FDSYNC command[RHEL-10])
- Resolves: RHEL-52599
  (CVE-2024-7409 qemu-kvm: Denial of Service via Improper Synchronization in QEMU NBD Server During Socket Closure [rhel-10.0])

* Tue Jul 30 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-6
- kvm-Enable-vhost-user-scmi-devices.patch [RHEL-50165]
- Resolves: RHEL-50165
  (Enable 'vhost-user-scmi-pci' and 'vhost-user-scmi' in qemu-kvm for RHIVOS)

* Wed Jul 24 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-5
- kvm-nbd-server-do-not-poll-within-a-coroutine-context.patch [RHEL-40959]
- kvm-nbd-server-Mark-negotiation-functions-as-coroutine_f.patch [RHEL-40959]
- kvm-qio-Inherit-follow_coroutine_ctx-across-TLS.patch [RHEL-40959]
- kvm-iotests-test-NBD-TLS-iothread.patch [RHEL-40959]
- Resolves: RHEL-40959
  (Qemu hang when quit dst vm after storage migration(nbd+tls))

* Thu Jul 04 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-4
- kvm-qcow2-Don-t-open-data_file-with-BDRV_O_NO_IO.patch [RHEL-46239]
- kvm-iotests-244-Don-t-store-data-file-with-protocol-in-i.patch [RHEL-46239]
- kvm-iotests-270-Don-t-store-data-file-with-json-prefix-i.patch [RHEL-46239]
- kvm-block-Parse-filenames-only-when-explicitly-requested.patch [RHEL-46239]
- Resolves: RHEL-46239
  (CVE-2024-4467 qemu-kvm: QEMU: 'qemu-img info' leads to host file read/write [rhel-10.0])

* Mon Jul 01 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-3
- kvm-qtest-x86-numa-test-do-not-use-the-obsolete-pentium-.patch [RHEL-28972]
- kvm-tests-qtest-libqtest-add-qtest_has_cpu_model-api.patch [RHEL-28972]
- kvm-tests-qtest-x86-check-for-availability-of-older-cpu-.patch [RHEL-28972]
- kvm-target-cpu-models-x86-Remove-the-existing-deprecated.patch [RHEL-28972]
- kvm-x86-cpu-deprecate-cpu-models-that-do-not-support-x86.patch [RHEL-28971]
- kvm-virtio-gpu-fix-v2-migration.patch [RHEL-36329]
- kvm-rhel-9.4.0-machine-type-compat-for-virtio-gpu-migrat.patch [RHEL-36329]
- kvm-s390x-remove-deprecated-rhel-machine-types.patch [RHEL-39898]
- kvm-s390x-select-correct-components-for-no-board-build.patch [RHEL-39898]
- kvm-target-s390x-Add-a-CONFIG-switch-to-disable-legacy-C.patch [RHEL-39898]
- kvm-target-s390x-cpu_models-Disable-everything-up-to-the.patch [RHEL-39898]
- kvm-target-s390x-Revert-the-old-s390x-CPU-model-disablem.patch [RHEL-39898]
- kvm-Revert-monitor-use-aio_co_reschedule_self.patch [RHEL-43409 RHEL-43410]
- kvm-aio-warn-about-iohandler_ctx-special-casing.patch [RHEL-43409 RHEL-43410]
- Resolves: RHEL-28972
  (x86: Remove the existing deprecated CPU models on RHEL10)
- Resolves: RHEL-28971
  (Consider deprecating CPU models like "Nehalem" / "IvyBridge" on RHEL 10)
- Resolves: RHEL-36329
  ([RHEL10.0.beta][stable_guest_abi]Failed to migrate VM with (qemu) qemu-kvm: Missing section footer for 0000:00:01.0/virtio-gpu qemu-kvm: load of migration failed: Invalid argument)
- Resolves: RHEL-39898
  (s390: Remove the legacy CPU models on RHEL10)
- Resolves: RHEL-43409
  (aio=io_uring: Assertion failure `luringcb->co->ctx == s->aio_context' with block_resize)
- Resolves: RHEL-43410
  (aio=native: Assertion failure `laiocb->co->ctx == laiocb->ctx->aio_context' with block_resize)

* Mon Jun 10 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-2
- kvm-Enable-vhost-user-snd-pci-device.patch [RHEL-37563]
- Resolves: RHEL-37563
  (Enable 'vhost-user-snd-pci' in qemu-kvm for RHIVOS)

* Tue May 14 2024 Miroslav Rezanina <mrezanin@redhat.com> - 9.0.0-1
- Rebase to QEMU 9.0.0 [RHEL-28852]
- Resolves: RHEL-28852
  (Rebase qemu-kvm to QEMU 9.0.0 for RHEL 10.0 beta)
- Resolves: RHEL-23771
  ([qemu-kvm] Disable passthrough of pmem device)
- Resolves: RHEL-34024
  (Remove RDMA migration support
- Resolves: RHEL-30366
  (Check/fix machine type compatibility for QEMU 9.0.0 [x86_64][rhel-10.0 Beta])
- Resolves: RHEL-30367
  (Check/fix machine type compatibility for QEMU 9.0.0 [aarch64][rhel-10.0 Beta])

* Tue Jan 02 2024 Miroslav Rezanina <mrezanin@redhat.com> - 8.2.0-1
- Rebase to QEMU 8.2.0 [RHEL-14111]
- Fix machine type compatibility [RHEL-17067 RHEL-17068]
- Add 9.4.0 machine type [RHEL-17168 RHEL-19117 RHEL-19119]
- Resolves: RHEL-14111
  (Rebase qemu-kvm to QEMU 8.2.0)
- Resolves: RHEL-17067
  (Check/fix machine type compatibility for qemu-kvm 8.2.0 [s390x])
- Resolves: RHEL-17068
  (Check/fix machine type compatibility for qemu-kvm 8.2.0 [x86_64])
- Resolves: RHEL-17168
  (Introduce virt-rhel9.4.0 arm-virt machine type [aarch64])
- Resolves: RHEL-19117
  (Introduce virt-rhel9.4.0 arm-virt machine type [x86_64])
- Resolves: RHEL-19119
  (Introduce virt-rhel9.4.0 arm-virt machine type [s390x])
