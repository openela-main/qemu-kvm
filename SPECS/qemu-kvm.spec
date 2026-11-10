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
Version: 10.1.0
Release: 28%{?rcrel}%{?dist}%{?cc_suffix}
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
# Handling binary changes for MR 505
Source40: IORT
Source41: IORT.its_off
Source42: IORT.smmuv3-dev
Source43: IORT.smmuv3-legacy


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
Patch0014: 0014-Disable-virtio-net-pci-romfile-loading-on-riscv64.patch
Patch0015: 0015-Revert-meson-temporarily-disable-Wunused-function.patch
Patch0016: 0016-Enable-make-check.patch
Patch0017: 0017-vfio-cap-number-of-devices-that-can-be-assigned.patch
Patch0018: 0018-Add-support-statement-to-help-output.patch
Patch0019: 0019-Use-qemu-kvm-in-documentation-instead-of-qemu-system.patch
Patch0020: 0020-qcow2-Deprecation-warning-when-opening-v2-images-rw.patch
Patch0021: 0021-file-posix-Define-DM_MPATH_PROBE_PATHS.patch
# For RHEL-112882 - [DEV Task]: Assertion `core->delayed_causes == 0' failed with e1000e NIC
Patch22: kvm-e1000e-Prevent-crash-from-legacy-interrupt-firing-af.patch
# For RHEL-119368 - [rhel10] Backport "arm/kvm: report registers we failed to set"
Patch23: kvm-arm-kvm-report-registers-we-failed-to-set.patch
# For RHEL-116443 - qemu crash after hot-unplug disk from the multifunction enabled bus,crash point PCIDevice *vf = dev->exp.sriov_pf.vf[i]
Patch24: kvm-pcie_sriov-make-pcie_sriov_pf_exit-safe-on-non-SR-IO.patch
# For RHEL-120253 - Backport fixes for PDCM and ARCH_CAPABILITIES migration incompatibility
Patch25: kvm-target-i386-add-compatibility-property-for-arch_capa.patch
# For RHEL-120253 - Backport fixes for PDCM and ARCH_CAPABILITIES migration incompatibility
Patch26: kvm-target-i386-add-compatibility-property-for-pdcm-feat.patch
# For RHEL-104009 - [IBM 10.2 FEAT] KVM: Enhance machine type definition to include CPI and PCI passthru capabilities (qemu)
# For RHEL-105823 - Add new -rhel10.2.0 machine type to qemu-kvm [s390x]
# For RHEL-73008 - [IBM 10.2 FEAT] KVM: Implement Control Program Identification (qemu)
Patch27: kvm-qapi-machine-s390x-add-QAPI-event-SCLP_CPI_INFO_AVAI.patch
# For RHEL-104009 - [IBM 10.2 FEAT] KVM: Enhance machine type definition to include CPI and PCI passthru capabilities (qemu)
# For RHEL-105823 - Add new -rhel10.2.0 machine type to qemu-kvm [s390x]
# For RHEL-73008 - [IBM 10.2 FEAT] KVM: Implement Control Program Identification (qemu)
Patch28: kvm-tests-functional-add-tests-for-SCLP-event-CPI.patch
# For RHEL-104009 - [IBM 10.2 FEAT] KVM: Enhance machine type definition to include CPI and PCI passthru capabilities (qemu)
# For RHEL-105823 - Add new -rhel10.2.0 machine type to qemu-kvm [s390x]
# For RHEL-73008 - [IBM 10.2 FEAT] KVM: Implement Control Program Identification (qemu)
Patch29: kvm-redhat-Add-new-rhel9.8.0-and-rhel10.2.0-machine-type.patch
# For RHEL-118810 - [RHEL 10.2] Windows 11 VM fails to boot up with ramfb='on' with QEMU 10.1
Patch30: kvm-vfio-rename-field-to-num_initial_regions.patch
# For RHEL-118810 - [RHEL 10.2] Windows 11 VM fails to boot up with ramfb='on' with QEMU 10.1
Patch31: kvm-vfio-only-check-region-info-cache-for-initial-region.patch
# For RHEL-105826 - Add new -rhel10.2.0 machine type to qemu-kvm [aarch64]
# For RHEL-105828 - Add new -rhel10.2.0 machine type to qemu-kvm [x86_64]
Patch32: kvm-arm-create-new-rhel-10.2-specific-virt-machine-type.patch
# For RHEL-105826 - Add new -rhel10.2.0 machine type to qemu-kvm [aarch64]
# For RHEL-105828 - Add new -rhel10.2.0 machine type to qemu-kvm [x86_64]
Patch33: kvm-arm-create-new-rhel-9.8-specific-virt-machine-type.patch
# For RHEL-105826 - Add new -rhel10.2.0 machine type to qemu-kvm [aarch64]
# For RHEL-105828 - Add new -rhel10.2.0 machine type to qemu-kvm [x86_64]
Patch34: kvm-x86-create-new-rhel-10.2-specific-pc-q35-machine-typ.patch
# For RHEL-105826 - Add new -rhel10.2.0 machine type to qemu-kvm [aarch64]
# For RHEL-105828 - Add new -rhel10.2.0 machine type to qemu-kvm [x86_64]
Patch35: kvm-x86-create-new-rhel-9.8-specific-pc-q35-machine-type.patch
# For RHEL-101929 - enable 'usb-bot' device for proper support of USB CD-ROM drives via libvirt  
Patch36: kvm-rh-enable-CONFIG_USB_STORAGE_BOT.patch
# For RHEL-120116 - CVE-2025-11234 qemu-kvm: VNC WebSocket handshake use-after-free [rhel-10.2]
Patch37: kvm-io-move-websock-resource-release-to-close-method.patch
# For RHEL-120116 - CVE-2025-11234 qemu-kvm: VNC WebSocket handshake use-after-free [rhel-10.2]
Patch38: kvm-io-fix-use-after-free-in-websocket-handshake-code.patch
# For RHEL-126573 - VFIO migration using multifd should be disabled by default
Patch39: kvm-vfio-Disable-VFIO-migration-with-MultiFD-support.patch
# For RHEL-67323 - [aarch64] Support ACPI based PCI hotplug on ARM
Patch40: kvm-hw-arm-virt-Use-ACPI-PCI-hotplug-by-default-from-10..patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch41: kvm-hw-arm-smmu-common-Check-SMMU-has-PCIe-Root-Complex-.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch42: kvm-hw-arm-virt-acpi-build-Re-arrange-SMMUv3-IORT-build.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch43: kvm-hw-arm-virt-acpi-build-Update-IORT-for-multiple-smmu.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch44: kvm-hw-arm-virt-Factor-out-common-SMMUV3-dt-bindings-cod.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch45: kvm-hw-arm-virt-Add-an-SMMU_IO_LEN-macro.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch46: kvm-hw-pci-Introduce-pci_setup_iommu_per_bus-for-per-bus.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch47: kvm-hw-arm-virt-Allow-user-creatable-SMMUv3-dev-instanti.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch48: kvm-qemu-options.hx-Document-the-arm-smmuv3-device.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch49: kvm-bios-tables-test-Allow-for-smmuv3-test-data.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch50: kvm-qtest-bios-tables-test-Add-tests-for-legacy-smmuv3-a.patch
# For RHEL-73800 - NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1
Patch51: kvm-qtest-bios-tables-test-Update-tables-for-smmuv3-test.patch
Patch52: kvm-qtest-Do-not-run-bios-tables-test-on-aarch64.patch
# For RHEL-126708 - [RHEL 10]snp guest fail to boot with hugepage
Patch53: kvm-ram-block-attributes-fix-interaction-with-hugetlb-me.patch
# For RHEL-126708 - [RHEL 10]snp guest fail to boot with hugepage
Patch54: kvm-ram-block-attributes-Unify-the-retrieval-of-the-bloc.patch
# For RHEL-128085 - VM crashes during boot when virtio device is attached through vfio_ccw
Patch55: kvm-hw-s390x-Fix-a-possible-crash-with-passed-through-vi.patch
# For RHEL-130704 - [rhel10] Fix the typo under vfio-pci device's enable-migration option 
Patch56: kvm-Fix-the-typo-of-vfio-pci-device-s-enable-migration-o.patch
# For RHEL-120115 - The vf nic created using the IGB emulated nic can not obtain ip address 
Patch57: kvm-pcie_sriov-Fix-broken-MMIO-accesses-from-SR-IOV-VFs.patch
# For RHEL-130478 - Migration from RHEL 10.2 to RHEL 10.1 with virt-rhel10.0.0 machine type fails on Grace
Patch58: kvm-arm-fix-oob-access-in-compat-handling.patch
# For RHEL-129540 - Assertion failure on drain with iothread and I/O load
Patch59: kvm-block-backend-Fix-race-when-resuming-queued-requests.patch
# For RHEL-121543 - The VM hit io error when do S3-PR integration on the pass-through  failover multipath device
Patch60: kvm-file-posix-Handle-suspended-dm-multipath-better-for-.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch61: kvm-accel-Add-Meson-and-config-support-for-MSHV-accelera.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch62: kvm-target-i386-emulate-Allow-instruction-decoding-from-.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch63: kvm-target-i386-mshv-Add-x86-decoder-emu-implementation.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch64: kvm-hw-intc-Generalize-APIC-helper-names-from-kvm_-to-ac.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch65: kvm-include-hw-hyperv-Add-MSHV-ABI-header-definitions.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch66: kvm-linux-headers-linux-Add-mshv.h-headers.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch67: kvm-accel-mshv-Add-accelerator-skeleton.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch68: kvm-accel-mshv-Register-memory-region-listeners.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch69: kvm-accel-mshv-Initialize-VM-partition.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch70: kvm-treewide-rename-qemu_wait_io_event-qemu_wait_io_even.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch71: kvm-accel-mshv-Add-vCPU-creation-and-execution-loop.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch72: kvm-accel-mshv-Add-vCPU-signal-handling.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch73: kvm-target-i386-mshv-Add-CPU-create-and-remove-logic.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch74: kvm-target-i386-mshv-Implement-mshv_store_regs.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch75: kvm-target-i386-mshv-Implement-mshv_get_standard_regs.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch76: kvm-target-i386-mshv-Implement-mshv_get_special_regs.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch77: kvm-target-i386-mshv-Implement-mshv_arch_put_registers.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch78: kvm-target-i386-mshv-Set-local-interrupt-controller-stat.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch79: kvm-target-i386-mshv-Register-CPUID-entries-with-MSHV.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch80: kvm-target-i386-mshv-Register-MSRs-with-MSHV.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch81: kvm-target-i386-mshv-Integrate-x86-instruction-decoder-e.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch82: kvm-target-i386-mshv-Write-MSRs-to-the-hypervisor.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch83: kvm-target-i386-mshv-Implement-mshv_vcpu_run.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch84: kvm-accel-mshv-Handle-overlapping-mem-mappings.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch85: kvm-qapi-accel-Allow-to-query-mshv-capabilities.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch86: kvm-target-i386-mshv-Use-preallocated-page-for-hvcall.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch87: kvm-docs-Add-mshv-to-documentation.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch88: kvm-MAINTAINERS-Add-maintainers-for-mshv-accelerator.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch89: kvm-accel-mshv-initialize-thread-name.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch90: kvm-accel-mshv-use-return-value-of-handle_pio_str_read.patch
# For RHEL-134212 - [RHEL10.2] L1VH qemu downstream initial merge RHEL10.2
Patch91: kvm-monitor-generalize-query-mshv-info-mshv-to-query-acc.patch
# For RHEL-110003 - Expose block limits of block nodes in QMP and qemu-img
Patch92: kvm-block-Improve-comments-in-BlockLimits.patch
# For RHEL-110003 - Expose block limits of block nodes in QMP and qemu-img
Patch93: kvm-block-Expose-block-limits-for-images-in-QMP.patch
# For RHEL-110003 - Expose block limits of block nodes in QMP and qemu-img
Patch94: kvm-qemu-img-info-Optionally-show-block-limits.patch
# For RHEL-110003 - Expose block limits of block nodes in QMP and qemu-img
Patch95: kvm-qemu-img-info-Add-cache-mode-option.patch
# For RHEL-111853 - [Intel 10.0 FEAT] [SPR] TDX: Virt-QEMU: QEMU Support [rhel-10]
Patch96: kvm-rh-configs-enable-CONFIG_TDX-for-x86_64.patch
# For RHEL-108142 - QEMU crashes when stopping source VM during live migration
Patch97: kvm-block-Fix-BDS-use-after-free-during-shutdown.patch
# For RHEL-126707 - [qemu, rhel-10] increase default TSEG size
Patch98: kvm-fix-pc_rhel_10_2_compat_len.patch
# For RHEL-126707 - [qemu, rhel-10] increase default TSEG size
Patch99: kvm-q35-increase-default-tseg-size.patch
# For RHEL-139028 - Intel IOMMU VM freezes: "call_irq_handler: 3.37 No irq handler for vector"[rhel-10.2]
Patch100: kvm-hw-intc-ioapic-Fix-ACCEL_KERNEL_GSI_IRQFD_POSSIBLE-t.patch
# For RHEL-111853 - [Intel 10.0 FEAT] [SPR] TDX: Virt-QEMU: QEMU Support [rhel-10]
Patch101: kvm-redhat-allow-5-level-paging-for-TDX-VMs.patch
# For RHEL-79118 - [network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10]
Patch102: kvm-rbd-Run-co-BH-CB-in-the-coroutine-s-AioContext.patch
# For RHEL-79118 - [network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10]
Patch103: kvm-curl-Fix-coroutine-waking.patch
# For RHEL-79118 - [network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10]
Patch104: kvm-block-io-Take-reqs_lock-for-tracked_requests.patch
# For RHEL-79118 - [network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10]
Patch105: kvm-qcow2-Re-initialize-lock-in-invalidate_cache.patch
# For RHEL-79118 - [network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10]
Patch106: kvm-qcow2-Fix-cache_clean_timer.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch107: kvm-net-bundle-all-offloads-in-a-single-struct.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch108: kvm-linux-headers-deal-with-counted_by-annotation.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch109: kvm-linux-headers-Update-to-Linux-v6.17-rc1.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch110: kvm-virtio-introduce-extended-features-type.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch111: kvm-virtio-serialize-extended-features-state.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch112: kvm-virtio-add-support-for-negotiating-extended-features.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch113: kvm-virtio-pci-implement-support-for-extended-features.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch114: kvm-vhost-add-support-for-negotiating-extended-features.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch115: kvm-qmp-update-virtio-features-map-to-support-extended-f.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch116: kvm-vhost-backend-implement-extended-features-support.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch117: kvm-vhost-net-implement-extended-features-support.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch118: kvm-virtio-net-implement-extended-features-support.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch119: kvm-net-implement-tunnel-probing.patch
# For RHEL-143785 - backport support for GSO over UDP tunnel offload
Patch120: kvm-net-implement-UDP-tunnel-features-offloading.patch
# For RHEL-147425 - virtiofs: processes become stuck in request_wait_answer on virtiofs mounts
Patch121: kvm-vhost-user-make-vhost_set_vring_file-synchronous.patch
# For RHEL-132749 - Migrate SCSI PR state and preempt reservation upon live migration
Patch122: kvm-scsi-generalize-scsi_SG_IO_FROM_DEV-to-scsi_SG_IO.patch
# For RHEL-132749 - Migrate SCSI PR state and preempt reservation upon live migration
Patch123: kvm-scsi-add-error-reporting-to-scsi_SG_IO.patch
# For RHEL-132749 - Migrate SCSI PR state and preempt reservation upon live migration
Patch124: kvm-scsi-track-SCSI-reservation-state-for-live-migration.patch
# For RHEL-132749 - Migrate SCSI PR state and preempt reservation upon live migration
Patch125: kvm-scsi-save-load-SCSI-reservation-state.patch
# For RHEL-132749 - Migrate SCSI PR state and preempt reservation upon live migration
Patch126: kvm-docs-add-SCSI-migrate-pr-documentation.patch
# For RHEL-134989 - Hotplugged interface device can not be shown in the guest
# For RHEL-146584 - [RHEL-10.2][ARM]: Unable to Check the mem prefetched size on Guest
Patch127: kvm-Revert-hw-arm-virt-Use-ACPI-PCI-hotplug-by-default-f.patch
# For RHEL-153058 - Qemu crashes with "double free" during restore --reset-nvram with uefi-vars secure boot
Patch128: kvm-hw-uefi-add-variable-digest-to-vmstate.patch
# For RHEL-144004 - [rhel-10] Regression in BLOCK_IO_ERROR event delivery with (w|r)error setting of 'stop' or 'enospc' due to event rate limiting
Patch129: kvm-block-Never-drop-BLOCK_IO_ERROR-with-action-stop-for.patch
# For RHEL-155601 - Mirror job can miss writes during startup, corrupting the copy [rhel-10.2]
Patch130: kvm-mirror-Fix-missed-dirty-bitmap-writes-during-startup.patch
# For RHEL-158224 - qemu-kvm: disk writes of fewer bytes than requested is a retry condition, not necessarily an indication of ENOSPC [rhel-10.2]
Patch131: kvm-linux-aio-Put-all-parameters-into-qemu_laiocb.patch
# For RHEL-158224 - qemu-kvm: disk writes of fewer bytes than requested is a retry condition, not necessarily an indication of ENOSPC [rhel-10.2]
Patch132: kvm-linux-aio-Resubmit-tails-of-short-reads-writes.patch
# For RHEL-158224 - qemu-kvm: disk writes of fewer bytes than requested is a retry condition, not necessarily an indication of ENOSPC [rhel-10.2]
Patch133: kvm-block-io_uring-avoid-potentially-getting-stuck-after.patch
# For RHEL-158224 - qemu-kvm: disk writes of fewer bytes than requested is a retry condition, not necessarily an indication of ENOSPC [rhel-10.2]
Patch134: kvm-io-uring-Resubmit-tails-of-short-writes.patch
# For RHEL-114231 - Add stats-intervals support to --blockdev
Patch135: kvm-block-enable-stats-intervals-for-storage-devices.patch
# For RHEL-114231 - Add stats-intervals support to --blockdev
Patch136: kvm-qdev-Free-property-array-on-release.patch
# For RHEL-158212 - qemu-kvm doesn't retry SG-IO on 05/25/00 (ILLEGAL REQUEST / LOGICAL UNIT NOT SUPPORTED) [rhel-10.3]
Patch137: kvm-scsi-Don-t-consider-LOGICAL-UNIT-NOT-SUPPORTED-guest.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch138: kvm-hw-tpm-Factor-tpm_ppi_enabled-out.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch139: kvm-hw-tpm-Add-TPMIfClass-ppi_enabled-field.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch140: kvm-hw-tpm-Remove-CRBState-ppi_enabled-field.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch141: kvm-hw-tpm-Propagate-ppi_enabled-to-tpm_tis_reset-and-re.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch142: kvm-hw-tpm-Simplify-tpm_ppi_enabled.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch143: kvm-docs-specs-tpm-document-PPI-support-on-ARM64-virt.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch144: kvm-hw-acpi-tpm-parameterize-PPI-base-address-in-tpm_bui.patch
# For RHEL-112608 - [ARM64] Windows 11 VM should install without TPM Bypass
Patch145: kvm-hw-tpm-add-PPI-support-to-tpm-tis-device-for-ARM64-v.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch146: kvm-vmstate-Introduce-VMSTATE_VARRAY_INT32_ALLOC.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch147: kvm-target-arm-Move-compare_u64-to-helper.c.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch148: kvm-target-arm-Convert-init_cpreg_list-to-g_hash_table_f.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch149: kvm-target-arm-machine-Use-VMSTATE_VARRAY_INT32_ALLOC-fo.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch150: kvm-target-arm-kvm-Export-kvm_print_register_name.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch151: kvm-target-arm-kvm-Tweak-print_register_name-for-arm64-s.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch152: kvm-target-arm-machine-Trace-cpreg-names-which-do-not-ma.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch153: kvm-target-arm-machine-Trace-all-register-mismatches.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch154: kvm-target-arm-machine-Fix-detection-of-unknown-incoming.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch155: kvm-target-arm-cpu-Introduce-the-infrastructure-for-cpre.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch156: kvm-target-arm-machine-Handle-ToleranceNotOnBothEnds-mig.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch157: kvm-target-arm-machine-Handle-ToleranceOnlySrcTestValue-.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch158: kvm-target-arm-cpu64-Mitigate-migration-failures-due-to-.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch159: kvm-target-arm-cpu64-Define-cpreg-migration-tolerance-fo.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch160: kvm-target-arm-helper-Define-cpreg-migration-tolerance-f.patch
# For RHEL-174858 - [rhel10] Backport qemu cross-kernel migration mitigation series
Patch161: kvm-Revert-target-arm-Reinstate-bogus-AArch32-DBGDTRTX-r.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch162: kvm-hw-pci-host-gpex-acpi-Fix-_DSM-function-0-support-re.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch163: kvm-vfio-scsi-ui-Error-check-qio_channel_socket_connect_.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch164: kvm-vfio-igd-Enable-quirks-when-IGD-is-not-the-primary-d.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch165: kvm-vfio-Remove-vfio-amd-xgbe-device.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch166: kvm-vfio-Remove-vfio-calxeda-xgmac-device.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch167: kvm-hw-arm-virt-Include-system-system.h.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch168: kvm-vfio-Remove-vfio-platform.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch169: kvm-vfio-Move-vfio-region.h-under-hw-vfio.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch170: kvm-vfio-container-set-error-on-cpr-failure.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch171: kvm-vfio-Report-an-error-when-the-dma_max_mappings-limit.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch172: kvm-hw-vfio-user-add-x-pci-class-code.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch173: kvm-vfio-Introduce-helper-vfio_pci_from_vfio_device.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch174: kvm-vfio-vfio-container-base.h-update-VFIOContainerBase-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch175: kvm-vfio-vfio-container.h-update-VFIOContainer-declarati.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch176: kvm-hw-vfio-cpr-legacy.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch177: kvm-hw-vfio-container.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch178: kvm-vfio-spapr.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch179: kvm-vfio-vfio-container.h-rename-VFIOContainer-bcontaine.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch180: kvm-vfio-user-container.h-update-VFIOUserContainer-decla.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch181: kvm-vfio-container.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch182: kvm-vfio-user-container.h-rename-VFIOUserContainer-bcont.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch183: kvm-vfio-user-pci.c-update-VFIOUserPCIDevice-declaration.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch184: kvm-vfio-user-pci.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch185: kvm-vfio-user-pci.c-rename-VFIOUserPCIDevice-device-fiel.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch186: kvm-vfio-pci.h-update-VFIOPCIDevice-declaration.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch187: kvm-vfio-pci.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch188: kvm-vfio-pci-quirks.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch189: kvm-vfio-cpr.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch190: kvm-vfio-igd.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch191: kvm-vfio-user-pci.c-use-QOM-casts-where-appropriate2.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch192: kvm-vfio-pci.h-rename-VFIOPCIDevice-pdev-field-to-parent.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch193: kvm-treewide-handle-result-of-qio_channel_set_blocking.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch194: kvm-vfio-pci-Do-not-unparent-in-instance_finalize.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch195: kvm-vfio-Do-not-unparent-in-instance_finalize.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch196: kvm-include-hw-vfio-vfio-container.h-rename-VFIOContaine.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch197: kvm-include-hw-vfio-vfio-container-base.h-rename-VFIOCon.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch198: kvm-include-hw-vfio-vfio-container.h-rename-file-to-vfio.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch199: kvm-include-hw-vfio-vfio-container-base.h-rename-file-to.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch200: kvm-hw-vfio-container.c-rename-file-to-container-legacy..patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch201: kvm-hw-vfio-container-base.c-rename-file-to-container.c.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch202: kvm-vfio-iommufd.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch203: kvm-vfio-cpr-iommufd.c-use-QOM-casts-where-appropriate.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch204: kvm-vfio-vfio-iommufd.h-rename-VFIOContainer-bcontainer-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch205: kvm-vfio-spapr.c-use-QOM-casts-where-appropriate2.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch206: kvm-vfio-spapr.c-rename-VFIOContainer-bcontainer-field-t.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch207: kvm-vfio-pci.c-rename-vfio_instance_init-to-vfio_pci_ini.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch208: kvm-vfio-pci.c-rename-vfio_instance_finalize-to-vfio_pci.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch209: kvm-vfio-pci.c-rename-vfio_pci_dev_class_init-to-vfio_pc.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch210: kvm-vfio-pci.c-rename-vfio_pci_dev_info-to-vfio_pci_info.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch211: kvm-s390x-s390-pci-vfio.c-use-QOM-casts-where-appropriat.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch212: kvm-hw-vfio-types.h-rename-TYPE_VFIO_PCI_BASE-to-TYPE_VF.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch213: kvm-vfio-pci.c-rename-vfio_pci_base_dev_class_init-to-vf.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch214: kvm-vfio-pci.c-rename-vfio_pci_base_dev_info-to-vfio_pci.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch215: kvm-vfio-pci.c-rename-vfio_pci_dev_properties-to-vfio_pc.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch216: kvm-vfio-pci.c-rename-vfio_pci_dev_nohotplug_properties-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch217: kvm-vfio-pci.c-rename-vfio_pci_nohotplug_dev_class_init-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch218: kvm-vfio-pci.c-rename-vfio_pci_nohotplug_dev_info-to-vfi.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch219: kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_class_init-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch220: kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_properties-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch221: kvm-vfio-user-pci.c-rename-vfio_user_instance_init-to-vf.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch222: kvm-vfio-user-pci.c-rename-vfio_user_instance_finalize-t.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch223: kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_info-to-vfi.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch224: kvm-include-hw-vfio-vfio-device.h-fix-include-header-gua.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch225: kvm-vfio-Remove-workaround-for-kernel-DMA-unmap-overflow.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch226: kvm-system-iommufd-Use-uint64_t-type-for-IOVA-mapping-si.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch227: kvm-hw-vfio-Reorder-vfio_container_query_dirty_bitmap-tr.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch228: kvm-hw-vfio-Avoid-ram_addr_t-in-vfio_container_query_dir.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch229: kvm-hw-vfio-Use-uint64_t-for-IOVA-mapping-size-in-vfio_c.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch230: kvm-migration-push-Error-errp-into-vmstate_subsection_lo.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch231: kvm-migration-push-Error-errp-into-vmstate_load_state.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch232: kvm-migration-Remove-error-variant-of-vmstate_save_state.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch233: kvm-migration-multi-mode-notifier.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch234: kvm-migration-add-cpr_walk_fd.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch235: kvm-oslib-qemu_clear_cloexec.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch236: kvm-migration-cpr-exec-command-parameter.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch237: kvm-migration-cpr-exec-save-and-load.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch238: kvm-migration-cpr-exec-mode.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch239: kvm-migration-cpr-exec-docs.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch240: kvm-vfio-cpr-exec-mode.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch241: kvm-hw-vfio-listener-Include-missing-exec-target_page.h-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch242: kvm-hw-Remove-unnecessary-system-ram_addr.h-header.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch243: kvm-vfio-container-Remap-only-populated-parts-in-a-secti.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch244: kvm-vfio-cpr-legacy-drop-an-erroneous-assert.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch245: kvm-vfio-iommufd-Set-cpr.ioas_id-on-source-side-for-CPR-.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch246: kvm-vfio-iommufd-Restore-vbasedev-s-reference-to-hwpt-af.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch247: kvm-vfio-container-Support-unmap-all-in-one-ioctl.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch248: kvm-vfio-iommufd-Support-unmap-all-in-one-ioctl.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch249: kvm-vfio-listener-Add-an-assertion-for-unmap_all.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch250: kvm-vfio-Clean-up-includes.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch251: kvm-migration-set-correct-list-pointer-when-removing-not.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch252: kvm-vfio-user-simplify-vfio_user_process.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch253: kvm-vfio-user-clarify-partial-message-handling.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch254: kvm-vfio-user-refactor-out-header-handling.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch255: kvm-vfio-user-simplify-vfio_user_recv_one.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch256: kvm-vfio-user-recycle-msg-on-failure.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch257: kvm-include-hw-hyperv-Remove-unused-struct-mshv_vp_regis.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch258: kvm-linux-headers-Update-to-Linux-v6.18-rc3.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch259: kvm-linux-headers-Update-to-Linux-v6.19-rc1.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch260: kvm-hw-vfio-Add-helper-to-retrieve-device-feature.patch
# For RHEL-138494 - NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3
Patch261: kvm-hw-vfio-region-Create-dmabuf-for-PCI-BAR-per-region.patch
# For RHEL-178767 - MSHV backport onto QEMU 10.1.0 is not able to launch MSHV guests
Patch262: kvm-accel-mshv-Remove-remap-overlapping-mappings-code.patch
# For RHEL-178767 - MSHV backport onto QEMU 10.1.0 is not able to launch MSHV guests
Patch263: kvm-accel-mshv-implement-cpu_thread_is_idle-hook.patch
# For RHEL-155807 - live migration failed the VM just register key only [rhel-10.3]
Patch264: kvm-scsi-adjust-error_prepend-formatting.patch
# For RHEL-155807 - live migration failed the VM just register key only [rhel-10.3]
Patch265: kvm-scsi-always-send-valid-PREEMPT-TYPE-field.patch
# For RHEL-155807 - live migration failed the VM just register key only [rhel-10.3]
Patch266: kvm-scsi-register-again-after-PREEMPT-without-reservatio.patch
# For RHEL-178846 - [aarch64] qemu-kvm crashes on --device tpm-tis-device,?
Patch267: kvm-hw-tpm-tpm_tis_sysbus-defer-resource-allocation-to-r.patch
# For RHEL-180750 - Backport in QEMU : vfio/container: Restrict dma_map_file() to shared RAM or RAM devices
Patch268: kvm-vfio-container-Restrict-dma_map_file-to-shared-RAM-o.patch
# For RHEL-153123 - live migration failed or get failed WSFC test result during WSFC testing [rhel-10.3]
Patch269: kvm-scsi-change-buf_size-to-unsigned-int-in-scsi_SG_IO.patch
# For RHEL-153123 - live migration failed or get failed WSFC test result during WSFC testing [rhel-10.3]
Patch270: kvm-scsi-handle-reservation-changes-across-migration.patch
# For RHEL-150900 - NVIDIA:Grace:Backport hw/vfio: Enable hugepfnmap for non-power-of-2 device memory regions - RHEL 10.3
Patch271: kvm-hw-vfio-sort-and-validate-sparse-mmap-regions-by-off.patch
# For RHEL-150900 - NVIDIA:Grace:Backport hw/vfio: Enable hugepfnmap for non-power-of-2 device memory regions - RHEL 10.3
Patch272: kvm-vfio-Add-Error-parameter-to-vfio_region_setup.patch
# For RHEL-150900 - NVIDIA:Grace:Backport hw/vfio: Enable hugepfnmap for non-power-of-2 device memory regions - RHEL 10.3
Patch273: kvm-hw-vfio-align-mmap-to-power-of-2-of-region-size-for-.patch
# For RHEL-184530 - CVE-2026-48914 qemu-kvm: Heap buffer overflow in virtio-blk SCSI request handling [rhel-10.3]
Patch274: kvm-virtio-blk-add-missing-VIRTIO_BLK_T_SCSI_CMD-size-ch.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch275: kvm-blkdebug-Add-delay-ns-option.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch276: kvm-block-Add-blk_co_start-end_request-and-BDRV_REQ_NO_Q.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch277: kvm-block-Add-flags-parameter-to-blk_-_pdiscard.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch278: kvm-ide-Minimal-fix-for-deadlock-between-TRIM-and-drain.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch279: kvm-ide-Clean-up-ide_trim_co_entry-to-be-idiomatic-corou.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch280: kvm-ide-test-Factor-out-wait_dma_completion.patch
# For RHEL-121686 - qemu-kvm hung during drain after double pause
Patch281: kvm-ide-test-Test-reset-during-TRIM.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch282: kvm-block-graph-lock-fix-missed-wakeup-in-bdrv_graph_co_.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch283: kvm-block-curl-fix-curl-internal-handles-handling.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch284: kvm-block-curl.c-Use-explicit-long-constants-in-curl_eas.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch285: kvm-block-curl.c-Fix-CURLOPT_VERBOSE-parameter-type.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch286: kvm-block-curl-fix-concurrent-completion-handling.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch287: kvm-block-curl-free-s-password-in-cleanup-paths.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch288: kvm-nvme-Kick-and-check-completions-in-BDS-context.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch289: kvm-nvme-Note-in-which-AioContext-some-functions-run.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch290: kvm-block-remove-detached-header-option-from-opts-after-.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch291: kvm-block-fix-luks-amend-when-run-in-coroutine.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch292: kvm-qed-Don-t-try-to-flush-during-incoming-migration.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch293: kvm-block-vmdk-fix-OOB-read-in-vmdk_read_extent.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch294: kvm-block-throttle-groups-fix-deadlock-with-iolimits-and.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch295: kvm-throttle-group-Fix-race-condition-in-throttle_group_.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch296: kvm-qemu-img-Fix-amend-option-parse-error-handling.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch297: kvm-qemu-img-rebase-don-t-exceed-IO_BUF_SIZE-in-one-oper.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch298: kvm-python-backport-drop-Python3.6-workarounds.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch299: kvm-python-backport-Remove-deprecated-get_event_loop-cal.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch300: kvm-python-backport-avoid-creating-additional-event-loop.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch301: kvm-iotests-147-ensure-temporary-sockets-are-closed-befo.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch302: kvm-iotests-151-ensure-subprocesses-are-cleaned-up.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch303: kvm-tests-qemu-iotest-fix-iotest-024-with-qed-images.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch304: kvm-tests-qemu-iotests-Fix-check-for-existing-file-in-_r.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch305: kvm-async-access-bottom-half-flags-with-qatomic_read.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch306: kvm-block-linux-aio-bound-ioq_submit-recursion-depth.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch307: kvm-block-io-fallback-to-bounce-buffer-if-BLKZEROOUT-is-.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch308: kvm-file-posix-populate-pwrite_zeroes_alignment.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch309: kvm-block-use-pwrite_zeroes_alignment-when-writing-first.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch310: kvm-iotests-add-Linux-loop-device-image-creation-test.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch311: kvm-virtio-Fix-crash-when-sriov-pf-is-set-for-non-PCI-Ex.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch312: kvm-virtio-scsi-pass-the-same-cdb_size-to-virtio_scsi_po.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch313: kvm-hw-scsi-avoid-deadlock-upon-TMF-request-cancelling-w.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch314: kvm-virtio-blk-fix-zone-report-buffer-out-of-memory-CVE-.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch315: kvm-ide-Fix-potential-assertion-failure-on-VM-stop-for-P.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch316: kvm-block-Create-DEFAULT_BLOCK_CONF-macro.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch317: kvm-block-Add-more-defaults-to-DEFAULT_BLOCK_CONF.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch318: kvm-block-mirror-check-range-when-setting-zero-bitmap-fo.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch319: kvm-iotests-test-active-mirror-with-unaligned-small-writ.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch320: kvm-block-mirror-fix-assertion-failure-upon-duplicate-co.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch321: kvm-commit-Drain-nodes-across-all-of-bdrv_commit.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch322: kvm-qemu-io-Add-aio_discard-command.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch323: kvm-qcow2-Fix-corruption-on-discard-during-write-with-CO.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch324: kvm-iotests-046-Test-that-discard-write_zeroes-wait-for-.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch325: kvm-qcow2-Fix-data-loss-on-zero-write-with-detect-zeroes.patch
# For RHEL-186384 - virt-storage: Backport stable branch fixes
Patch326: kvm-block-Fix-crash-after-setting-latency-historygram-wi.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch327: kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vio.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch328: kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vde.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch329: kvm-hw-arm-smmu-common-Factor-out-common-helper-function.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch330: kvm-hw-arm-smmu-add-memory-regions-as-property-for-an-SM.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch331: kvm-hw-arm-smmuv3-Extract-common-definitions-to-smmuv3-c.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch332: kvm-hw-arm-smmu-common-Make-iommu-ops-part-of-SMMUState.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch333: kvm-hw-arm-smmuv3-accel-Introduce-smmuv3-accel-device.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch334: kvm-hw-arm-smmuv3-accel-Initialize-shared-system-address.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch335: kvm-hw-pci-pci-Move-pci_init_bus_master-after-adding-dev.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch336: kvm-hw-pci-Export-pci_device_get_iommu_bus_devfn-and-ret.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch337: kvm-hw-pci-pci-Add-optional-supports_address_space-callb.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch338: kvm-hw-pci-bridge-pci_expander_bridge-Move-TYPE_PXB_PCIE.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch339: kvm-hw-arm-smmuv3-accel-Restrict-accelerated-SMMUv3-to-v.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch340: kvm-hw-arm-smmuv3-Implement-get_viommu_cap-callback.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch341: kvm-hw-pci-Introduce-pci_device_get_viommu_flags.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch342: kvm-hw-pci-Introduce-pci_device_get_host_iommu_quirks.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch343: kvm-hw-arm-smmuv3-common-Define-STE-CD-fields-via-regist.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch344: kvm-hw-arm-smmuv3-common-Add-NSCFG-bit-definition-for-CD.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch345: kvm-hw-arm-smmuv3-common-Add-STE-CD-set-helpers-for-repe.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch346: kvm-hw-arm-smmuv3-accel-Add-set-unset_iommu_device-callb.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch347: kvm-hw-arm-smmuv3-propagate-smmuv3_cmdq_consume-errors-t.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch348: kvm-hw-arm-smmuv3-accel-Add-nested-vSTE-install-uninstal.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch349: kvm-hw-arm-smmuv3-accel-Install-SMMUv3-GBPA-based-hwpt.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch350: kvm-hw-pci-pci-Introduce-a-callback-to-retrieve-the-MSI-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch351: kvm-hw-arm-smmuv3-accel-Implement-get_msi_direct_gpa-cal.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch352: kvm-hw-arm-virt-Set-msi-gpa-property.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch353: kvm-hw-arm-smmuv3-accel-Add-support-to-issue-invalidatio.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch354: kvm-hw-arm-smmuv3-Initialize-ID-registers-early-during-r.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch355: kvm-hw-arm-smmuv3-accel-Get-host-SMMUv3-hw-info-and-vali.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch356: kvm-hw-pci-host-gpex-Allow-to-generate-preserve-boot-con.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch357: kvm-hw-arm-virt-Set-PCI-preserve_config-for-accel-SMMUv3.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch358: kvm-tests-qtest-bios-tables-test-Prepare-for-IORT-reviso.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch359: kvm-hw-arm-virt-acpi-build-Add-IORT-RMR-regions-to-handl.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch360: kvm-tests-qtest-bios-tables-test-Update-IORT-blobs-after.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch361: kvm-hw-arm-smmuv3-Block-migration-when-accel-is-enabled.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch362: kvm-hw-arm-smmuv3-Add-accel-property-for-SMMUv3-device.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch363: kvm-hw-arm-smmuv3-accel-Add-a-property-to-specify-RIL-su.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch364: kvm-hw-arm-smmuv3-accel-Add-support-for-ATS.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch365: kvm-hw-arm-smmuv3-accel-Add-property-to-specify-OAS-bits.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch366: kvm-backends-iommufd-Retrieve-PASID-width-from-iommufd_b.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch367: kvm-backends-iommufd-Add-get_pasid_info-callback.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch368: kvm-hw-pci-Add-helper-to-insert-PCIe-extended-capability.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch369: kvm-hw-pci-Factor-out-common-PASID-capability-initializa.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch370: kvm-hw-vfio-pci-Synthesize-PASID-capability-for-vfio-pci.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch371: kvm-hw-arm-smmuv3-accel-Make-SubstreamID-support-configu.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch372: kvm-system-memory-Factor-address_space_is_io-out.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch373: kvm-target-i386-arch_memory_mapping-Use-address_space_me.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch374: kvm-hw-s390x-sclp-Use-address_space_memory_is_io-in-sclp.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch375: kvm-system-physmem-Remove-cpu_physical_memory_is_io.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch376: kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vev.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch377: kvm-hw-arm-smmuv3-accel-Add-viommu-free-helper.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch378: kvm-hw-arm-smmuv3-accel-Allocate-vEVENTQ-for-accelerated.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch379: kvm-hw-arm-smmuv3-Introduce-a-helper-function-for-event-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch380: kvm-hw-arm-smmuv3-accel-Read-and-propagate-host-vIOMMU-e.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch381: kvm-hw-arm-smmuv3-Correct-SMMUEN-field-name-in-CR0.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch382: kvm-hw-arm-smmuv3-Fix-CFGI_CD-handling-when-stage-1-is-u.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch383: kvm-hw-arm-smmuv3-accel-Check-ATS-compatibility-between-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch384: kvm-hw-arm-smmuv3-accel-Change-ats-property-type-to-OnOf.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch385: kvm-hw-arm-smmuv3-accel-Change-ril-property-type-to-OnOf.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch386: kvm-qdev-Add-a-SsidSizeMode-property-type.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch387: kvm-hw-arm-smmuv3-accel-Change-ssidsize-property-type-to.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch388: kvm-qdev-Add-an-OasMode-property-type.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch389: kvm-hw-arm-smmuv3-accel-Change-oas-property-type-to-OasM.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch390: kvm-qemu-options.hx-Document-arm-smmuv3-device-s-accel-p.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch391: kvm-hw-arm-smmuv3-Have-smmuv3_accel_init-take-an-Error-p.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch392: kvm-hw-arm-smmuv3-Update-ATC-invalidation-check.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch393: kvm-hw-arm-smmuv3-Improve-accel-SMMUv3-usage-documentati.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch394: kvm-hw-arm-smmuv3-accel-Add-helper-for-resolving-auto-pa.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch395: kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ats.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch396: kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ril.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch397: kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ssidsiz.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch398: kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-oas.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch399: kvm-hw-arm-smmuv3-Set-default-ats-ril-ssidsize-oas-to-au.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch400: kvm-qemu-options.hx-Support-auto-for-accel-SMMUv3-proper.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch401: kvm-hw-pci-pci-Enforce-pci_setup_iommu_per_bus-is-called.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch402: kvm-vfio-iommufd-Force-creating-nesting-parent-HWPT.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch403: kvm-hw-vfio-iommufd-Control-dirty-tracking-for-nesting-p.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch404: kvm-backends-iommufd-Update-iommufd_backend_get_device_i.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch405: kvm-iommufd-Rename-all-the-idev-and-idevc-variables-to-h.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch406: kvm-backends-iommufd-Update-iommufd_backend_alloc_viommu.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch407: kvm-backends-iommufd-Introduce-iommufd_backend_alloc_hw_.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch408: kvm-backends-iommufd-Introduce-iommufd_backend_viommu_mm.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch409: kvm-system-iommufd-Remove-unused-viommu-pointer-from-IOM.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch410: kvm-hw-arm-smmuv3-accel-Introduce-CMDQV-ops-interface.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch411: kvm-hw-arm-smmuv3-Avoid-including-CONFIG_DEVICES-in-hw-h.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch412: kvm-hw-arm-tegra241-cmdqv-Add-Tegra241-CMDQV-ops-backend.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch413: kvm-hw-arm-smmuv3-accel-Wire-CMDQV-ops-into-accel-lifecy.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch414: kvm-hw-arm-virt-Use-stored-SMMUv3-device-list-for-IORT-b.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch415: kvm-hw-arm-tegra241-cmdqv-Probe-host-Tegra241-CMDQV-supp.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch416: kvm-hw-arm-tegra241-cmdqv-Implement-CMDQV-init.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch417: kvm-hw-arm-virt-Link-SMMUv3-CMDQV-resources-to-platform-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch418: kvm-hw-arm-tegra241-cmdqv-Implement-CMDQV-vIOMMU-alloc-f.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch419: kvm-hw-arm-tegra241-cmdqv-mmap-host-VINTF-Page0-for-CMDQ.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch420: kvm-hw-arm-tegra241-cmdqv-Emulate-CMDQ-V-Config-region.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch421: kvm-hw-arm-tegra241-cmdqv-Emulate-VCMDQ-register-reads.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch422: kvm-hw-arm-tegra241-cmdqv-Emulate-VCMDQ-register-writes.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch423: kvm-hw-arm-tegra241-cmdqv-Allocate-HW-VCMDQs-once-config.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch424: kvm-hw-arm-tegra241-cmdqv-Route-allocated-VCMDQ-Page0-ac.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch425: kvm-memory-Allow-RAM-device-regions-to-skip-IOMMU-mappin.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch426: kvm-hw-arm-tegra241-cmdqv-Use-mmap-d-host-VINTF-page0-fo.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch427: kvm-hw-arm-smmuv3-accel-Introduce-common-helper-for-veve.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch428: kvm-hw-arm-tegra241-cmdqv-Read-and-propagate-Tegra241-CM.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch429: kvm-hw-arm-tegra241-cmdqv-Initialize-register-state-on-r.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch430: kvm-hw-arm-tegra241-cmdqv-Limit-queue-size-based-on-back.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch431: kvm-hw-arm-smmuv3-Add-per-device-identifier-property.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch432: kvm-hw-arm-smmuv3-accel-Introduce-helper-to-query-CMDQV-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch433: kvm-hw-arm-virt-acpi-Advertise-Tegra241-CMDQV-nodes-in-D.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch434: kvm-hw-arm-smmuv3-accel-Enforce-viommu-association-when-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch435: kvm-hw-arm-tegra241-cmdqv-Document-the-CMDQV-design-and-.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch436: kvm-hw-arm-smmuv3-Add-cmdqv-property-for-SMMUv3-device.patch
# For RHEL-142465 - [RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus
# For RHEL-160190 - NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3
# For RHEL-163596 - NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3
# For RHEL-73794 - NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1
# For RHEL-73796 - NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1
# For RHEL-73798 - NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1
Patch437: kvm-rh-aarch64-rh-devices.mak-Add-CONFIG_TEGRA241_CMDQV.patch
# For RHEL-113894 - [RHEL.10.2][virual network] Hit qemu coredump when removed an interface that the guest is using from the host
Patch438: kvm-net-tap-linux.c-avoid-abort-when-setting-invalid-fd.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch439: kvm-crypto-only-verify-CA-certs-in-chain-of-trust.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch440: kvm-crypto-remove-extraneous-pointer-usage-in-gnutls-cer.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch441: kvm-crypto-fix-error-reporting-in-cert-chain-checks.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch442: kvm-crypto-allow-client-server-cert-chains.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch443: kvm-crypto-stop-requiring-key-encipherment-usage-in-x509.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch444: kvm-crypto-switch-to-newer-gnutls-API-for-distinguished-.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch445: kvm-crypto-remove-redundant-parameter-checking-CA-certs.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch446: kvm-crypto-add-missing-free-of-certs-array.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch447: kvm-crypto-replace-stat-with-access-for-credential-check.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch448: kvm-crypto-remove-redundant-access-checks-before-loading.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch449: kvm-crypto-move-check-for-TLS-creds-dir-property.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch450: kvm-crypto-use-g_autofree-when-loading-x509-credentials.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch451: kvm-crypto-remove-needless-indirection-via-parent_obj-fi.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch452: kvm-crypto-move-release-of-DH-parameters-into-TLS-creds-.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch453: kvm-crypto-shorten-the-endpoint-server-check-in-TLS-cred.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch454: kvm-crypto-remove-duplication-loading-x509-CA-cert.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch455: kvm-crypto-reduce-duplication-in-handling-TLS-priority-s.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch456: kvm-crypto-introduce-method-for-reloading-TLS-creds.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch457: kvm-crypto-introduce-a-wrapper-around-gnutls-credentials.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch458: kvm-crypto-fix-lifecycle-handling-of-gnutls-credentials-.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch459: kvm-crypto-make-TLS-credentials-structs-private.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch460: kvm-crypto-deprecate-use-of-external-dh-params.pem-file.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch461: kvm-crypto-avoid-loading-the-CA-certs-twice.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch462: kvm-crypto-avoid-loading-the-identity-certs-twice.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch463: kvm-crypto-expand-logic-to-cope-with-multiple-certificat.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch464: kvm-crypto-support-upto-5-parallel-certificate-identitie.patch
# For RHEL-111934 - QEMU support for loading multiple sets of x509 certs for PQC hybrid mode
Patch465: kvm-docs-creation-of-x509-certs-compliant-with-post-quan.patch
# For RHEL-184675 - NVIDIA:Backport vfio/pci: add vfio-pci ATS control property - RHEL 10.3
Patch466: kvm-iommufd-Introduce-handler-for-device-ATS-support.patch
# For RHEL-184675 - NVIDIA:Backport vfio/pci: add vfio-pci ATS control property - RHEL 10.3
Patch467: kvm-vfio-pci-Add-ats-property.patch
# For RHEL-180837 - [aarch64] Live migration of TPM-equipped guests fails: Unknown ramblock "tpm-ppi" (qemu-kvm-10.1.0-19.el10 → older builds)
Patch468: kvm-hw-core-platform-bus-guard-platform_bus_get_mmio_add.patch
# For RHEL-180837 - [aarch64] Live migration of TPM-equipped guests fails: Unknown ramblock "tpm-ppi" (qemu-kvm-10.1.0-19.el10 → older builds)
Patch469: kvm-hw-tpm-gate-PPI-support-on-tpm-tis-device-behind-a-d.patch
# For RHEL-180837 - [aarch64] Live migration of TPM-equipped guests fails: Unknown ramblock "tpm-ppi" (qemu-kvm-10.1.0-19.el10 → older builds)
Patch470: kvm-hw-tpm-default-tpm-tis-device-PPI-to-disabled.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch471: kvm-s390x-css-limit-number-of-CHPIDs-in-description.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch472: kvm-s390x-ioinst-Require-strict-length-and-format-for-SE.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch473: kvm-s390x-pci-Shrink-RPCIT-ranges-to-registered-window.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch474: kvm-s390x-pci-Tighten-region-detection-for-BAR-read-writ.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch475: kvm-s390x-sclp-reject-invalid-write-event-data-headers.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch476: kvm-s390x-kvm-clamp-stsi-3.2.2-size.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch477: kvm-s390x-sclp-prevent-re-reading-the-sclp-header.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch478: kvm-s390x-sclpcpi-check-event-length-field-before-readin.patch
# For RHEL-192791 - RHEL10.0 - qemu s390x: interface harding fixes
Patch479: kvm-s390x-css-firm-up-handling-of-chained-TIC-CCWs.patch
# For RHEL-224652 - Backport  vfio/region: Clarify dma-buf failure messages 
Patch480: kvm-vfio-region-Clarify-dma-buf-failure-messages.patch
# For RHEL-151317 - RHEL10 - KVM full Boot order support -- Guest is crashing for the invalid boot device(<boot order='1'/> -- add-on qcow2 file)
Patch481: kvm-pc-bios-s390-ccw-Always-reset-virtio-device-on-faile.patch
# For RHEL-246035 - [RHEL10.3] Exhausted DMA bounce buffer on building cuda-samples in VM
Patch482: kvm-system-memory-Use-memmove-for-directly-accessible-re.patch
# For RHEL-246035 - [RHEL10.3] Exhausted DMA bounce buffer on building cuda-samples in VM
Patch483: kvm-system-memory-Use-qemu_ram_move-for-directly-accessi.patch
# For RHEL-246035 - [RHEL10.3] Exhausted DMA bounce buffer on building cuda-samples in VM
Patch484: kvm-system-memory-Make-ram-device-region-directly-access.patch

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

Install this package if you want access to the qemu tests, 
or qemu-iotests.


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

# Handling binary changes for MR 505
cp %{SOURCE40} %{SOURCE41} %{SOURCE42} %{SOURCE43} tests/data/acpi/aarch64/virt/

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
mkdir -p %{buildroot}%{testsdir}/tests/qemu-iotests
mkdir -p %{buildroot}%{testsdir}/scripts/qmp


install -m 0644 scripts/dump-guest-memory.py \
                %{buildroot}%{_datadir}/%{name}


# Install qemu.py and qmp/ scripts required to run tests
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
rm -rf %{buildroot}%{_datadir}/%{name}/dtb/petalogix*.dtb
rm -f %{buildroot}%{_datadir}/%{name}/dtb/bamboo.dtb
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
rm -rf %{buildroot}%{_datadir}/%{name}/dtb/canyonlands.dtb
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
rm -rf %{buildroot}%{_datadir}/%{name}/ast27x0_bootrom.bin

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
* Mon Aug 24 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-28
- kvm-system-memory-Use-memmove-for-directly-accessible-re.patch [RHEL-246035]
- kvm-system-memory-Use-qemu_ram_move-for-directly-accessi.patch [RHEL-246035]
- kvm-system-memory-Make-ram-device-region-directly-access.patch [RHEL-246035]
- Resolves: RHEL-246035
  ([RHEL10.3] Exhausted DMA bounce buffer on building cuda-samples in VM)

* Thu Aug 20 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-27
- kvm-pc-bios-s390-ccw-Always-reset-virtio-device-on-faile.patch [RHEL-151317]
- Resolves: RHEL-151317
  (RHEL10 - KVM full Boot order support -- Guest is crashing for the invalid boot device(<boot order='1'/> -- add-on qcow2 file))

* Tue Aug 11 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-26
- kvm-vfio-region-Clarify-dma-buf-failure-messages.patch [RHEL-224652]
- Resolves: RHEL-224652
  (Backport  vfio/region: Clarify dma-buf failure messages )

* Mon Aug 03 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-25
- kvm-hw-core-platform-bus-guard-platform_bus_get_mmio_add.patch [RHEL-180837]
- kvm-hw-tpm-gate-PPI-support-on-tpm-tis-device-behind-a-d.patch [RHEL-180837]
- kvm-hw-tpm-default-tpm-tis-device-PPI-to-disabled.patch [RHEL-180837]
- kvm-s390x-css-limit-number-of-CHPIDs-in-description.patch [RHEL-192791]
- kvm-s390x-ioinst-Require-strict-length-and-format-for-SE.patch [RHEL-192791]
- kvm-s390x-pci-Shrink-RPCIT-ranges-to-registered-window.patch [RHEL-192791]
- kvm-s390x-pci-Tighten-region-detection-for-BAR-read-writ.patch [RHEL-192791]
- kvm-s390x-sclp-reject-invalid-write-event-data-headers.patch [RHEL-192791]
- kvm-s390x-kvm-clamp-stsi-3.2.2-size.patch [RHEL-192791]
- kvm-s390x-sclp-prevent-re-reading-the-sclp-header.patch [RHEL-192791]
- kvm-s390x-sclpcpi-check-event-length-field-before-readin.patch [RHEL-192791]
- kvm-s390x-css-firm-up-handling-of-chained-TIC-CCWs.patch [RHEL-192791]
- Resolves: RHEL-180837
  ([aarch64] Live migration of TPM-equipped guests fails: Unknown ramblock "tpm-ppi" (qemu-kvm-10.1.0-19.el10 → older builds))
- Resolves: RHEL-192791
  (RHEL10.0 - qemu s390x: interface harding fixes)

* Fri Jul 10 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-24
- kvm-net-tap-linux.c-avoid-abort-when-setting-invalid-fd.patch [RHEL-113894]
- kvm-crypto-only-verify-CA-certs-in-chain-of-trust.patch [RHEL-111934]
- kvm-crypto-remove-extraneous-pointer-usage-in-gnutls-cer.patch [RHEL-111934]
- kvm-crypto-fix-error-reporting-in-cert-chain-checks.patch [RHEL-111934]
- kvm-crypto-allow-client-server-cert-chains.patch [RHEL-111934]
- kvm-crypto-stop-requiring-key-encipherment-usage-in-x509.patch [RHEL-111934]
- kvm-crypto-switch-to-newer-gnutls-API-for-distinguished-.patch [RHEL-111934]
- kvm-crypto-remove-redundant-parameter-checking-CA-certs.patch [RHEL-111934]
- kvm-crypto-add-missing-free-of-certs-array.patch [RHEL-111934]
- kvm-crypto-replace-stat-with-access-for-credential-check.patch [RHEL-111934]
- kvm-crypto-remove-redundant-access-checks-before-loading.patch [RHEL-111934]
- kvm-crypto-move-check-for-TLS-creds-dir-property.patch [RHEL-111934]
- kvm-crypto-use-g_autofree-when-loading-x509-credentials.patch [RHEL-111934]
- kvm-crypto-remove-needless-indirection-via-parent_obj-fi.patch [RHEL-111934]
- kvm-crypto-move-release-of-DH-parameters-into-TLS-creds-.patch [RHEL-111934]
- kvm-crypto-shorten-the-endpoint-server-check-in-TLS-cred.patch [RHEL-111934]
- kvm-crypto-remove-duplication-loading-x509-CA-cert.patch [RHEL-111934]
- kvm-crypto-reduce-duplication-in-handling-TLS-priority-s.patch [RHEL-111934]
- kvm-crypto-introduce-method-for-reloading-TLS-creds.patch [RHEL-111934]
- kvm-crypto-introduce-a-wrapper-around-gnutls-credentials.patch [RHEL-111934]
- kvm-crypto-fix-lifecycle-handling-of-gnutls-credentials-.patch [RHEL-111934]
- kvm-crypto-make-TLS-credentials-structs-private.patch [RHEL-111934]
- kvm-crypto-deprecate-use-of-external-dh-params.pem-file.patch [RHEL-111934]
- kvm-crypto-avoid-loading-the-CA-certs-twice.patch [RHEL-111934]
- kvm-crypto-avoid-loading-the-identity-certs-twice.patch [RHEL-111934]
- kvm-crypto-expand-logic-to-cope-with-multiple-certificat.patch [RHEL-111934]
- kvm-crypto-support-upto-5-parallel-certificate-identitie.patch [RHEL-111934]
- kvm-docs-creation-of-x509-certs-compliant-with-post-quan.patch [RHEL-111934]
- kvm-iommufd-Introduce-handler-for-device-ATS-support.patch [RHEL-184675]
- kvm-vfio-pci-Add-ats-property.patch [RHEL-184675]
- Resolves: RHEL-113894
  ([RHEL.10.2][virual network] Hit qemu coredump when removed an interface that the guest is using from the host)
- Resolves: RHEL-111934
  (QEMU support for loading multiple sets of x509 certs for PQC hybrid mode)
- Resolves: RHEL-184675
  (NVIDIA:Backport vfio/pci: add vfio-pci ATS control property - RHEL 10.3)

* Mon Jun 29 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-23
- kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vio.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vde.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmu-common-Factor-out-common-helper-function.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmu-add-memory-regions-as-property-for-an-SM.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Extract-common-definitions-to-smmuv3-c.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmu-common-Make-iommu-ops-part-of-SMMUState.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Introduce-smmuv3-accel-device.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Initialize-shared-system-address.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-pci-Move-pci_init_bus_master-after-adding-dev.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-Export-pci_device_get_iommu_bus_devfn-and-ret.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-pci-Add-optional-supports_address_space-callb.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-bridge-pci_expander_bridge-Move-TYPE_PXB_PCIE.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Restrict-accelerated-SMMUv3-to-v.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Implement-get_viommu_cap-callback.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-Introduce-pci_device_get_viommu_flags.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-Introduce-pci_device_get_host_iommu_quirks.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-common-Define-STE-CD-fields-via-regist.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-common-Add-NSCFG-bit-definition-for-CD.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-common-Add-STE-CD-set-helpers-for-repe.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-set-unset_iommu_device-callb.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-propagate-smmuv3_cmdq_consume-errors-t.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-nested-vSTE-install-uninstal.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Install-SMMUv3-GBPA-based-hwpt.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-pci-Introduce-a-callback-to-retrieve-the-MSI-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Implement-get_msi_direct_gpa-cal.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-Set-msi-gpa-property.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-support-to-issue-invalidatio.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Initialize-ID-registers-early-during-r.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Get-host-SMMUv3-hw-info-and-vali.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-host-gpex-Allow-to-generate-preserve-boot-con.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-Set-PCI-preserve_config-for-accel-SMMUv3.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-tests-qtest-bios-tables-test-Prepare-for-IORT-reviso.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-acpi-build-Add-IORT-RMR-regions-to-handl.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-tests-qtest-bios-tables-test-Update-IORT-blobs-after.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Block-migration-when-accel-is-enabled.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Add-accel-property-for-SMMUv3-device.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-a-property-to-specify-RIL-su.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-support-for-ATS.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-property-to-specify-OAS-bits.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Retrieve-PASID-width-from-iommufd_b.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Add-get_pasid_info-callback.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-Add-helper-to-insert-PCIe-extended-capability.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-Factor-out-common-PASID-capability-initializa.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-vfio-pci-Synthesize-PASID-capability-for-vfio-pci.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Make-SubstreamID-support-configu.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-system-memory-Factor-address_space_is_io-out.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-target-i386-arch_memory_mapping-Use-address_space_me.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-s390x-sclp-Use-address_space_memory_is_io-in-sclp.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-system-physmem-Remove-cpu_physical_memory_is_io.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Introduce-iommufd_backend_alloc_vev.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-viommu-free-helper.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Allocate-vEVENTQ-for-accelerated.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Introduce-a-helper-function-for-event-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Read-and-propagate-host-vIOMMU-e.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Correct-SMMUEN-field-name-in-CR0.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Fix-CFGI_CD-handling-when-stage-1-is-u.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Check-ATS-compatibility-between-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Change-ats-property-type-to-OnOf.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Change-ril-property-type-to-OnOf.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-qdev-Add-a-SsidSizeMode-property-type.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Change-ssidsize-property-type-to.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-qdev-Add-an-OasMode-property-type.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Change-oas-property-type-to-OasM.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-qemu-options.hx-Document-arm-smmuv3-device-s-accel-p.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Have-smmuv3_accel_init-take-an-Error-p.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Update-ATC-invalidation-check.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Improve-accel-SMMUv3-usage-documentati.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Add-helper-for-resolving-auto-pa.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ats.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ril.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-ssidsiz.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Implement-auto-value-for-oas.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Set-default-ats-ril-ssidsize-oas-to-au.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-qemu-options.hx-Support-auto-for-accel-SMMUv3-proper.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-pci-pci-Enforce-pci_setup_iommu_per_bus-is-called.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-vfio-iommufd-Force-creating-nesting-parent-HWPT.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-vfio-iommufd-Control-dirty-tracking-for-nesting-p.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Update-iommufd_backend_get_device_i.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-iommufd-Rename-all-the-idev-and-idevc-variables-to-h.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Update-iommufd_backend_alloc_viommu.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Introduce-iommufd_backend_alloc_hw_.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-backends-iommufd-Introduce-iommufd_backend_viommu_mm.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-system-iommufd-Remove-unused-viommu-pointer-from-IOM.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Introduce-CMDQV-ops-interface.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Avoid-including-CONFIG_DEVICES-in-hw-h.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Add-Tegra241-CMDQV-ops-backend.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Wire-CMDQV-ops-into-accel-lifecy.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-Use-stored-SMMUv3-device-list-for-IORT-b.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Probe-host-Tegra241-CMDQV-supp.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Implement-CMDQV-init.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-Link-SMMUv3-CMDQV-resources-to-platform-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Implement-CMDQV-vIOMMU-alloc-f.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-mmap-host-VINTF-Page0-for-CMDQ.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Emulate-CMDQ-V-Config-region.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Emulate-VCMDQ-register-reads.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Emulate-VCMDQ-register-writes.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Allocate-HW-VCMDQs-once-config.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Route-allocated-VCMDQ-Page0-ac.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-memory-Allow-RAM-device-regions-to-skip-IOMMU-mappin.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Use-mmap-d-host-VINTF-page0-fo.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Introduce-common-helper-for-veve.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Read-and-propagate-Tegra241-CM.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Initialize-register-state-on-r.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Limit-queue-size-based-on-back.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Add-per-device-identifier-property.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Introduce-helper-to-query-CMDQV-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-virt-acpi-Advertise-Tegra241-CMDQV-nodes-in-D.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-accel-Enforce-viommu-association-when-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-tegra241-cmdqv-Document-the-CMDQV-design-and-.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-hw-arm-smmuv3-Add-cmdqv-property-for-SMMUv3-device.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- kvm-rh-aarch64-rh-devices.mak-Add-CONFIG_TEGRA241_CMDQV.patch [RHEL-142465 RHEL-160190 RHEL-163596 RHEL-73794 RHEL-73796 RHEL-73798]
- Resolves: RHEL-142465
  ([RHEL-10.1][ARM]: Two smmuv3 devices can be attached to the same bus)
- Resolves: RHEL-160190
  (NVIDIA:Backport hw/arm/smmuv3-accel: Support AUTO properties - RHEL 10.3)
- Resolves: RHEL-163596
  (NVIDIA:Backport hw/arm/smmuv3-accel: Resolve AUTO properties - RHEL 10.3)
- Resolves: RHEL-73794
  (NVIDIA:Grace-Hopper:Backport HW accelerated nesting support for arm SMMUv3 - RHEL 10.1)
- Resolves: RHEL-73796
  (NVIDIA:Grace-Hopper:Backport vEVENTQ support for smmuv3 - RHEL 10.1)
- Resolves: RHEL-73798
  (NVIDIA:Grace-Hopper:Backport CMDQV support - RHEL 10.1)

* Tue Jun 23 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-22
- kvm-blkdebug-Add-delay-ns-option.patch [RHEL-121686]
- kvm-block-Add-blk_co_start-end_request-and-BDRV_REQ_NO_Q.patch [RHEL-121686]
- kvm-block-Add-flags-parameter-to-blk_-_pdiscard.patch [RHEL-121686]
- kvm-ide-Minimal-fix-for-deadlock-between-TRIM-and-drain.patch [RHEL-121686]
- kvm-ide-Clean-up-ide_trim_co_entry-to-be-idiomatic-corou.patch [RHEL-121686]
- kvm-ide-test-Factor-out-wait_dma_completion.patch [RHEL-121686]
- kvm-ide-test-Test-reset-during-TRIM.patch [RHEL-121686]
- kvm-block-graph-lock-fix-missed-wakeup-in-bdrv_graph_co_.patch [RHEL-186384]
- kvm-block-curl-fix-curl-internal-handles-handling.patch [RHEL-186384]
- kvm-block-curl.c-Use-explicit-long-constants-in-curl_eas.patch [RHEL-186384]
- kvm-block-curl.c-Fix-CURLOPT_VERBOSE-parameter-type.patch [RHEL-186384]
- kvm-block-curl-fix-concurrent-completion-handling.patch [RHEL-186384]
- kvm-block-curl-free-s-password-in-cleanup-paths.patch [RHEL-186384]
- kvm-nvme-Kick-and-check-completions-in-BDS-context.patch [RHEL-186384]
- kvm-nvme-Note-in-which-AioContext-some-functions-run.patch [RHEL-186384]
- kvm-block-remove-detached-header-option-from-opts-after-.patch [RHEL-186384]
- kvm-block-fix-luks-amend-when-run-in-coroutine.patch [RHEL-186384]
- kvm-qed-Don-t-try-to-flush-during-incoming-migration.patch [RHEL-186384]
- kvm-block-vmdk-fix-OOB-read-in-vmdk_read_extent.patch [RHEL-186384]
- kvm-block-throttle-groups-fix-deadlock-with-iolimits-and.patch [RHEL-186384]
- kvm-throttle-group-Fix-race-condition-in-throttle_group_.patch [RHEL-186384]
- kvm-qemu-img-Fix-amend-option-parse-error-handling.patch [RHEL-186384]
- kvm-qemu-img-rebase-don-t-exceed-IO_BUF_SIZE-in-one-oper.patch [RHEL-186384]
- kvm-python-backport-drop-Python3.6-workarounds.patch [RHEL-186384]
- kvm-python-backport-Remove-deprecated-get_event_loop-cal.patch [RHEL-186384]
- kvm-python-backport-avoid-creating-additional-event-loop.patch [RHEL-186384]
- kvm-iotests-147-ensure-temporary-sockets-are-closed-befo.patch [RHEL-186384]
- kvm-iotests-151-ensure-subprocesses-are-cleaned-up.patch [RHEL-186384]
- kvm-tests-qemu-iotest-fix-iotest-024-with-qed-images.patch [RHEL-186384]
- kvm-tests-qemu-iotests-Fix-check-for-existing-file-in-_r.patch [RHEL-186384]
- kvm-async-access-bottom-half-flags-with-qatomic_read.patch [RHEL-186384]
- kvm-block-linux-aio-bound-ioq_submit-recursion-depth.patch [RHEL-186384]
- kvm-block-io-fallback-to-bounce-buffer-if-BLKZEROOUT-is-.patch [RHEL-186384]
- kvm-file-posix-populate-pwrite_zeroes_alignment.patch [RHEL-186384]
- kvm-block-use-pwrite_zeroes_alignment-when-writing-first.patch [RHEL-186384]
- kvm-iotests-add-Linux-loop-device-image-creation-test.patch [RHEL-186384]
- kvm-virtio-Fix-crash-when-sriov-pf-is-set-for-non-PCI-Ex.patch [RHEL-186384]
- kvm-virtio-scsi-pass-the-same-cdb_size-to-virtio_scsi_po.patch [RHEL-186384]
- kvm-hw-scsi-avoid-deadlock-upon-TMF-request-cancelling-w.patch [RHEL-186384]
- kvm-virtio-blk-fix-zone-report-buffer-out-of-memory-CVE-.patch [RHEL-186384]
- kvm-ide-Fix-potential-assertion-failure-on-VM-stop-for-P.patch [RHEL-186384]
- kvm-block-Create-DEFAULT_BLOCK_CONF-macro.patch [RHEL-186384]
- kvm-block-Add-more-defaults-to-DEFAULT_BLOCK_CONF.patch [RHEL-186384]
- kvm-block-mirror-check-range-when-setting-zero-bitmap-fo.patch [RHEL-186384]
- kvm-iotests-test-active-mirror-with-unaligned-small-writ.patch [RHEL-186384]
- kvm-block-mirror-fix-assertion-failure-upon-duplicate-co.patch [RHEL-186384]
- kvm-commit-Drain-nodes-across-all-of-bdrv_commit.patch [RHEL-186384]
- kvm-qemu-io-Add-aio_discard-command.patch [RHEL-186384]
- kvm-qcow2-Fix-corruption-on-discard-during-write-with-CO.patch [RHEL-186384]
- kvm-iotests-046-Test-that-discard-write_zeroes-wait-for-.patch [RHEL-186384]
- kvm-qcow2-Fix-data-loss-on-zero-write-with-detect-zeroes.patch [RHEL-186384]
- kvm-block-Fix-crash-after-setting-latency-historygram-wi.patch [RHEL-186384]
- Resolves: RHEL-121686
  (qemu-kvm hung during drain after double pause)
- Resolves: RHEL-186384
  (virt-storage: Backport stable branch fixes)

* Fri Jun 19 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-21
- kvm-hw-vfio-sort-and-validate-sparse-mmap-regions-by-off.patch [RHEL-150900]
- kvm-vfio-Add-Error-parameter-to-vfio_region_setup.patch [RHEL-150900]
- kvm-hw-vfio-align-mmap-to-power-of-2-of-region-size-for-.patch [RHEL-150900]
- kvm-virtio-blk-add-missing-VIRTIO_BLK_T_SCSI_CMD-size-ch.patch [RHEL-184530]
- Resolves: RHEL-150900
  (NVIDIA:Grace:Backport hw/vfio: Enable hugepfnmap for non-power-of-2 device memory regions - RHEL 10.3)
- Resolves: RHEL-184530
  (CVE-2026-48914 qemu-kvm: Heap buffer overflow in virtio-blk SCSI request handling [rhel-10.3])

* Mon Jun 08 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-20
- kvm-accel-mshv-Remove-remap-overlapping-mappings-code.patch [RHEL-178767]
- kvm-accel-mshv-implement-cpu_thread_is_idle-hook.patch [RHEL-178767]
- kvm-scsi-adjust-error_prepend-formatting.patch [RHEL-155807]
- kvm-scsi-always-send-valid-PREEMPT-TYPE-field.patch [RHEL-155807]
- kvm-scsi-register-again-after-PREEMPT-without-reservatio.patch [RHEL-155807]
- kvm-hw-tpm-tpm_tis_sysbus-defer-resource-allocation-to-r.patch [RHEL-178846]
- kvm-vfio-container-Restrict-dma_map_file-to-shared-RAM-o.patch [RHEL-180750]
- kvm-scsi-change-buf_size-to-unsigned-int-in-scsi_SG_IO.patch [RHEL-153123]
- kvm-scsi-handle-reservation-changes-across-migration.patch [RHEL-153123]
- Resolves: RHEL-178767
  (MSHV backport onto QEMU 10.1.0 is not able to launch MSHV guests)
- Resolves: RHEL-155807
  (live migration failed the VM just register key only [rhel-10.3])
- Resolves: RHEL-178846
  ([aarch64] qemu-kvm crashes on --device tpm-tis-device,?)
- Resolves: RHEL-180750
  (Backport in QEMU : vfio/container: Restrict dma_map_file() to shared RAM or RAM devices)
- Resolves: RHEL-153123
  (live migration failed or get failed WSFC test result during WSFC testing [rhel-10.3])

* Tue May 26 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-19
- kvm-vmstate-Introduce-VMSTATE_VARRAY_INT32_ALLOC.patch [RHEL-174858]
- kvm-target-arm-Move-compare_u64-to-helper.c.patch [RHEL-174858]
- kvm-target-arm-Convert-init_cpreg_list-to-g_hash_table_f.patch [RHEL-174858]
- kvm-target-arm-machine-Use-VMSTATE_VARRAY_INT32_ALLOC-fo.patch [RHEL-174858]
- kvm-target-arm-kvm-Export-kvm_print_register_name.patch [RHEL-174858]
- kvm-target-arm-kvm-Tweak-print_register_name-for-arm64-s.patch [RHEL-174858]
- kvm-target-arm-machine-Trace-cpreg-names-which-do-not-ma.patch [RHEL-174858]
- kvm-target-arm-machine-Trace-all-register-mismatches.patch [RHEL-174858]
- kvm-target-arm-machine-Fix-detection-of-unknown-incoming.patch [RHEL-174858]
- kvm-target-arm-cpu-Introduce-the-infrastructure-for-cpre.patch [RHEL-174858]
- kvm-target-arm-machine-Handle-ToleranceNotOnBothEnds-mig.patch [RHEL-174858]
- kvm-target-arm-machine-Handle-ToleranceOnlySrcTestValue-.patch [RHEL-174858]
- kvm-target-arm-cpu64-Mitigate-migration-failures-due-to-.patch [RHEL-174858]
- kvm-target-arm-cpu64-Define-cpreg-migration-tolerance-fo.patch [RHEL-174858]
- kvm-target-arm-helper-Define-cpreg-migration-tolerance-f.patch [RHEL-174858]
- kvm-Revert-target-arm-Reinstate-bogus-AArch32-DBGDTRTX-r.patch [RHEL-174858]
- kvm-hw-pci-host-gpex-acpi-Fix-_DSM-function-0-support-re.patch [RHEL-138494]
- kvm-vfio-scsi-ui-Error-check-qio_channel_socket_connect_.patch [RHEL-138494]
- kvm-vfio-igd-Enable-quirks-when-IGD-is-not-the-primary-d.patch [RHEL-138494]
- kvm-vfio-Remove-vfio-amd-xgbe-device.patch [RHEL-138494]
- kvm-vfio-Remove-vfio-calxeda-xgmac-device.patch [RHEL-138494]
- kvm-hw-arm-virt-Include-system-system.h.patch [RHEL-138494]
- kvm-vfio-Remove-vfio-platform.patch [RHEL-138494]
- kvm-vfio-Move-vfio-region.h-under-hw-vfio.patch [RHEL-138494]
- kvm-vfio-container-set-error-on-cpr-failure.patch [RHEL-138494]
- kvm-vfio-Report-an-error-when-the-dma_max_mappings-limit.patch [RHEL-138494]
- kvm-hw-vfio-user-add-x-pci-class-code.patch [RHEL-138494]
- kvm-vfio-Introduce-helper-vfio_pci_from_vfio_device.patch [RHEL-138494]
- kvm-vfio-vfio-container-base.h-update-VFIOContainerBase-.patch [RHEL-138494]
- kvm-vfio-vfio-container.h-update-VFIOContainer-declarati.patch [RHEL-138494]
- kvm-hw-vfio-cpr-legacy.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-hw-vfio-container.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-spapr.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-vfio-container.h-rename-VFIOContainer-bcontaine.patch [RHEL-138494]
- kvm-vfio-user-container.h-update-VFIOUserContainer-decla.patch [RHEL-138494]
- kvm-vfio-container.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-user-container.h-rename-VFIOUserContainer-bcont.patch [RHEL-138494]
- kvm-vfio-user-pci.c-update-VFIOUserPCIDevice-declaration.patch [RHEL-138494]
- kvm-vfio-user-pci.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-VFIOUserPCIDevice-device-fiel.patch [RHEL-138494]
- kvm-vfio-pci.h-update-VFIOPCIDevice-declaration.patch [RHEL-138494]
- kvm-vfio-pci.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-pci-quirks.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-cpr.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-igd.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-user-pci.c-use-QOM-casts-where-appropriate2.patch [RHEL-138494]
- kvm-vfio-pci.h-rename-VFIOPCIDevice-pdev-field-to-parent.patch [RHEL-138494]
- kvm-treewide-handle-result-of-qio_channel_set_blocking.patch [RHEL-138494]
- kvm-vfio-pci-Do-not-unparent-in-instance_finalize.patch [RHEL-138494]
- kvm-vfio-Do-not-unparent-in-instance_finalize.patch [RHEL-138494]
- kvm-include-hw-vfio-vfio-container.h-rename-VFIOContaine.patch [RHEL-138494]
- kvm-include-hw-vfio-vfio-container-base.h-rename-VFIOCon.patch [RHEL-138494]
- kvm-include-hw-vfio-vfio-container.h-rename-file-to-vfio.patch [RHEL-138494]
- kvm-include-hw-vfio-vfio-container-base.h-rename-file-to.patch [RHEL-138494]
- kvm-hw-vfio-container.c-rename-file-to-container-legacy..patch [RHEL-138494]
- kvm-hw-vfio-container-base.c-rename-file-to-container.c.patch [RHEL-138494]
- kvm-vfio-iommufd.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-cpr-iommufd.c-use-QOM-casts-where-appropriate.patch [RHEL-138494]
- kvm-vfio-vfio-iommufd.h-rename-VFIOContainer-bcontainer-.patch [RHEL-138494]
- kvm-vfio-spapr.c-use-QOM-casts-where-appropriate2.patch [RHEL-138494]
- kvm-vfio-spapr.c-rename-VFIOContainer-bcontainer-field-t.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_instance_init-to-vfio_pci_ini.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_instance_finalize-to-vfio_pci.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_dev_class_init-to-vfio_pc.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_dev_info-to-vfio_pci_info.patch [RHEL-138494]
- kvm-s390x-s390-pci-vfio.c-use-QOM-casts-where-appropriat.patch [RHEL-138494]
- kvm-hw-vfio-types.h-rename-TYPE_VFIO_PCI_BASE-to-TYPE_VF.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_base_dev_class_init-to-vf.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_base_dev_info-to-vfio_pci.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_dev_properties-to-vfio_pc.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_dev_nohotplug_properties-.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_nohotplug_dev_class_init-.patch [RHEL-138494]
- kvm-vfio-pci.c-rename-vfio_pci_nohotplug_dev_info-to-vfi.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_class_init-.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_properties-.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-vfio_user_instance_init-to-vf.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-vfio_user_instance_finalize-t.patch [RHEL-138494]
- kvm-vfio-user-pci.c-rename-vfio_user_pci_dev_info-to-vfi.patch [RHEL-138494]
- kvm-include-hw-vfio-vfio-device.h-fix-include-header-gua.patch [RHEL-138494]
- kvm-vfio-Remove-workaround-for-kernel-DMA-unmap-overflow.patch [RHEL-138494]
- kvm-system-iommufd-Use-uint64_t-type-for-IOVA-mapping-si.patch [RHEL-138494]
- kvm-hw-vfio-Reorder-vfio_container_query_dirty_bitmap-tr.patch [RHEL-138494]
- kvm-hw-vfio-Avoid-ram_addr_t-in-vfio_container_query_dir.patch [RHEL-138494]
- kvm-hw-vfio-Use-uint64_t-for-IOVA-mapping-size-in-vfio_c.patch [RHEL-138494]
- kvm-migration-push-Error-errp-into-vmstate_subsection_lo.patch [RHEL-138494]
- kvm-migration-push-Error-errp-into-vmstate_load_state.patch [RHEL-138494]
- kvm-migration-Remove-error-variant-of-vmstate_save_state.patch [RHEL-138494]
- kvm-migration-multi-mode-notifier.patch [RHEL-138494]
- kvm-migration-add-cpr_walk_fd.patch [RHEL-138494]
- kvm-oslib-qemu_clear_cloexec.patch [RHEL-138494]
- kvm-migration-cpr-exec-command-parameter.patch [RHEL-138494]
- kvm-migration-cpr-exec-save-and-load.patch [RHEL-138494]
- kvm-migration-cpr-exec-mode.patch [RHEL-138494]
- kvm-migration-cpr-exec-docs.patch [RHEL-138494]
- kvm-vfio-cpr-exec-mode.patch [RHEL-138494]
- kvm-hw-vfio-listener-Include-missing-exec-target_page.h-.patch [RHEL-138494]
- kvm-hw-Remove-unnecessary-system-ram_addr.h-header.patch [RHEL-138494]
- kvm-vfio-container-Remap-only-populated-parts-in-a-secti.patch [RHEL-138494]
- kvm-vfio-cpr-legacy-drop-an-erroneous-assert.patch [RHEL-138494]
- kvm-vfio-iommufd-Set-cpr.ioas_id-on-source-side-for-CPR-.patch [RHEL-138494]
- kvm-vfio-iommufd-Restore-vbasedev-s-reference-to-hwpt-af.patch [RHEL-138494]
- kvm-vfio-container-Support-unmap-all-in-one-ioctl.patch [RHEL-138494]
- kvm-vfio-iommufd-Support-unmap-all-in-one-ioctl.patch [RHEL-138494]
- kvm-vfio-listener-Add-an-assertion-for-unmap_all.patch [RHEL-138494]
- kvm-vfio-Clean-up-includes.patch [RHEL-138494]
- kvm-migration-set-correct-list-pointer-when-removing-not.patch [RHEL-138494]
- kvm-vfio-user-simplify-vfio_user_process.patch [RHEL-138494]
- kvm-vfio-user-clarify-partial-message-handling.patch [RHEL-138494]
- kvm-vfio-user-refactor-out-header-handling.patch [RHEL-138494]
- kvm-vfio-user-simplify-vfio_user_recv_one.patch [RHEL-138494]
- kvm-vfio-user-recycle-msg-on-failure.patch [RHEL-138494]
- kvm-include-hw-hyperv-Remove-unused-struct-mshv_vp_regis.patch [RHEL-138494]
- kvm-linux-headers-Update-to-Linux-v6.18-rc3.patch [RHEL-138494]
- kvm-linux-headers-Update-to-Linux-v6.19-rc1.patch [RHEL-138494]
- kvm-hw-vfio-Add-helper-to-retrieve-device-feature.patch [RHEL-138494]
- kvm-hw-vfio-region-Create-dmabuf-for-PCI-BAR-per-region.patch [RHEL-138494]
- Resolves: RHEL-174858
  ([rhel10] Backport qemu cross-kernel migration mitigation series)
- Resolves: RHEL-138494
  (NVIDIA:Grace-Hopper:Backport vfio: Add DMABUF support for PCI BAR regions - RHEL 10.3)

* Mon May 11 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-18
- kvm-scsi-Don-t-consider-LOGICAL-UNIT-NOT-SUPPORTED-guest.patch [RHEL-158212]
- kvm-hw-tpm-Factor-tpm_ppi_enabled-out.patch [RHEL-112608]
- kvm-hw-tpm-Add-TPMIfClass-ppi_enabled-field.patch [RHEL-112608]
- kvm-hw-tpm-Remove-CRBState-ppi_enabled-field.patch [RHEL-112608]
- kvm-hw-tpm-Propagate-ppi_enabled-to-tpm_tis_reset-and-re.patch [RHEL-112608]
- kvm-hw-tpm-Simplify-tpm_ppi_enabled.patch [RHEL-112608]
- kvm-docs-specs-tpm-document-PPI-support-on-ARM64-virt.patch [RHEL-112608]
- kvm-hw-acpi-tpm-parameterize-PPI-base-address-in-tpm_bui.patch [RHEL-112608]
- kvm-hw-tpm-add-PPI-support-to-tpm-tis-device-for-ARM64-v.patch [RHEL-112608]
- Resolves: RHEL-158212
  (qemu-kvm doesn't retry SG-IO on 05/25/00 (ILLEGAL REQUEST / LOGICAL UNIT NOT SUPPORTED) [rhel-10.3])
- Resolves: RHEL-112608
  ([ARM64] Windows 11 VM should install without TPM Bypass)

* Tue Apr 21 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-17
- kvm-block-enable-stats-intervals-for-storage-devices.patch [RHEL-114231]
- kvm-qdev-Free-property-array-on-release.patch [RHEL-114231]
- Resolves: RHEL-114231
  (Add stats-intervals support to --blockdev)

* Mon Mar 30 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-16
- kvm-linux-aio-Put-all-parameters-into-qemu_laiocb.patch [RHEL-158224]
- kvm-linux-aio-Resubmit-tails-of-short-reads-writes.patch [RHEL-158224]
- kvm-block-io_uring-avoid-potentially-getting-stuck-after.patch [RHEL-158224]
- kvm-io-uring-Resubmit-tails-of-short-writes.patch [RHEL-158224]
- Resolves: RHEL-158224
  (qemu-kvm: disk writes of fewer bytes than requested is a retry condition, not necessarily an indication of ENOSPC [rhel-10.2])

* Thu Mar 26 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-15
- kvm-mirror-Fix-missed-dirty-bitmap-writes-during-startup.patch [RHEL-155601]
- Resolves: RHEL-155601
  (Mirror job can miss writes during startup, corrupting the copy [rhel-10.2])

* Wed Mar 18 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-14
- kvm-hw-uefi-add-variable-digest-to-vmstate.patch [RHEL-153058]
- kvm-block-Never-drop-BLOCK_IO_ERROR-with-action-stop-for.patch [RHEL-144004]
- Resolves: RHEL-153058
  (Qemu crashes with "double free" during restore --reset-nvram with uefi-vars secure boot)
- Resolves: RHEL-144004
  ([rhel-10] Regression in BLOCK_IO_ERROR event delivery with (w|r)error setting of 'stop' or 'enospc' due to event rate limiting)

* Thu Feb 19 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-13
- kvm-vhost-user-make-vhost_set_vring_file-synchronous.patch [RHEL-147425]
- kvm-scsi-generalize-scsi_SG_IO_FROM_DEV-to-scsi_SG_IO.patch [RHEL-132749]
- kvm-scsi-add-error-reporting-to-scsi_SG_IO.patch [RHEL-132749]
- kvm-scsi-track-SCSI-reservation-state-for-live-migration.patch [RHEL-132749]
- kvm-scsi-save-load-SCSI-reservation-state.patch [RHEL-132749]
- kvm-docs-add-SCSI-migrate-pr-documentation.patch [RHEL-132749]
- kvm-Revert-hw-arm-virt-Use-ACPI-PCI-hotplug-by-default-f.patch [RHEL-134989 RHEL-146584]
- Resolves: RHEL-147425
  (virtiofs: processes become stuck in request_wait_answer on virtiofs mounts)
- Resolves: RHEL-132749
  (Migrate SCSI PR state and preempt reservation upon live migration)
- Resolves: RHEL-134989
  (Hotplugged interface device can not be shown in the guest)
- Resolves: RHEL-146584
  ([RHEL-10.2][ARM]: Unable to Check the mem prefetched size on Guest)

* Mon Feb 02 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-12
- kvm-rbd-Run-co-BH-CB-in-the-coroutine-s-AioContext.patch [RHEL-79118]
- kvm-curl-Fix-coroutine-waking.patch [RHEL-79118]
- kvm-block-io-Take-reqs_lock-for-tracked_requests.patch [RHEL-79118]
- kvm-qcow2-Re-initialize-lock-in-invalidate_cache.patch [RHEL-79118]
- kvm-qcow2-Fix-cache_clean_timer.patch [RHEL-79118]
- kvm-net-bundle-all-offloads-in-a-single-struct.patch [RHEL-143785]
- kvm-linux-headers-deal-with-counted_by-annotation.patch [RHEL-143785]
- kvm-linux-headers-Update-to-Linux-v6.17-rc1.patch [RHEL-143785]
- kvm-virtio-introduce-extended-features-type.patch [RHEL-143785]
- kvm-virtio-serialize-extended-features-state.patch [RHEL-143785]
- kvm-virtio-add-support-for-negotiating-extended-features.patch [RHEL-143785]
- kvm-virtio-pci-implement-support-for-extended-features.patch [RHEL-143785]
- kvm-vhost-add-support-for-negotiating-extended-features.patch [RHEL-143785]
- kvm-qmp-update-virtio-features-map-to-support-extended-f.patch [RHEL-143785]
- kvm-vhost-backend-implement-extended-features-support.patch [RHEL-143785]
- kvm-vhost-net-implement-extended-features-support.patch [RHEL-143785]
- kvm-virtio-net-implement-extended-features-support.patch [RHEL-143785]
- kvm-net-implement-tunnel-probing.patch [RHEL-143785]
- kvm-net-implement-UDP-tunnel-features-offloading.patch [RHEL-143785]
- Resolves: RHEL-79118
  ([network-storage][rbd][core-dump]installation of guest failed sometimes with multiqueue enabled [rhel10])
- Resolves: RHEL-143785
  (backport support for GSO over UDP tunnel offload)

* Tue Jan 13 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-11
- kvm-fix-pc_rhel_10_2_compat_len.patch [RHEL-126707]
- kvm-q35-increase-default-tseg-size.patch [RHEL-126707]
- kvm-hw-intc-ioapic-Fix-ACCEL_KERNEL_GSI_IRQFD_POSSIBLE-t.patch [RHEL-139028]
- kvm-redhat-allow-5-level-paging-for-TDX-VMs.patch [RHEL-111853]
- Resolves: RHEL-126707
  ([qemu, rhel-10] increase default TSEG size)
- Resolves: RHEL-139028
  (Intel IOMMU VM freezes: "call_irq_handler: 3.37 No irq handler for vector"[rhel-10.2])
- Resolves: RHEL-111853
  ([Intel 10.0 FEAT] [SPR] TDX: Virt-QEMU: QEMU Support [rhel-10])

* Mon Jan 05 2026 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-10
- kvm-block-Fix-BDS-use-after-free-during-shutdown.patch [RHEL-108142]
- Resolves: RHEL-108142
  (QEMU crashes when stopping source VM during live migration)

* Mon Dec 15 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-9
- kvm-monitor-generalize-query-mshv-info-mshv-to-query-acc.patch [RHEL-134212]
- kvm-block-Improve-comments-in-BlockLimits.patch [RHEL-110003]
- kvm-block-Expose-block-limits-for-images-in-QMP.patch [RHEL-110003]
- kvm-qemu-img-info-Optionally-show-block-limits.patch [RHEL-110003]
- kvm-qemu-img-info-Add-cache-mode-option.patch [RHEL-110003]
- kvm-rh-configs-enable-CONFIG_TDX-for-x86_64.patch [RHEL-111853]
- Resolves: RHEL-134212
  ([RHEL10.2] L1VH qemu downstream initial merge RHEL10.2)
- Resolves: RHEL-110003
  (Expose block limits of block nodes in QMP and qemu-img)
- Resolves: RHEL-111853
  ([Intel 10.0 FEAT] [SPR] TDX: Virt-QEMU: QEMU Support [rhel-10])

* Tue Dec 09 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-8
- kvm-block-backend-Fix-race-when-resuming-queued-requests.patch [RHEL-129540]
- kvm-file-posix-Handle-suspended-dm-multipath-better-for-.patch [RHEL-121543]
- kvm-accel-Add-Meson-and-config-support-for-MSHV-accelera.patch [RHEL-134212]
- kvm-target-i386-emulate-Allow-instruction-decoding-from-.patch [RHEL-134212]
- kvm-target-i386-mshv-Add-x86-decoder-emu-implementation.patch [RHEL-134212]
- kvm-hw-intc-Generalize-APIC-helper-names-from-kvm_-to-ac.patch [RHEL-134212]
- kvm-include-hw-hyperv-Add-MSHV-ABI-header-definitions.patch [RHEL-134212]
- kvm-linux-headers-linux-Add-mshv.h-headers.patch [RHEL-134212]
- kvm-accel-mshv-Add-accelerator-skeleton.patch [RHEL-134212]
- kvm-accel-mshv-Register-memory-region-listeners.patch [RHEL-134212]
- kvm-accel-mshv-Initialize-VM-partition.patch [RHEL-134212]
- kvm-treewide-rename-qemu_wait_io_event-qemu_wait_io_even.patch [RHEL-134212]
- kvm-accel-mshv-Add-vCPU-creation-and-execution-loop.patch [RHEL-134212]
- kvm-accel-mshv-Add-vCPU-signal-handling.patch [RHEL-134212]
- kvm-target-i386-mshv-Add-CPU-create-and-remove-logic.patch [RHEL-134212]
- kvm-target-i386-mshv-Implement-mshv_store_regs.patch [RHEL-134212]
- kvm-target-i386-mshv-Implement-mshv_get_standard_regs.patch [RHEL-134212]
- kvm-target-i386-mshv-Implement-mshv_get_special_regs.patch [RHEL-134212]
- kvm-target-i386-mshv-Implement-mshv_arch_put_registers.patch [RHEL-134212]
- kvm-target-i386-mshv-Set-local-interrupt-controller-stat.patch [RHEL-134212]
- kvm-target-i386-mshv-Register-CPUID-entries-with-MSHV.patch [RHEL-134212]
- kvm-target-i386-mshv-Register-MSRs-with-MSHV.patch [RHEL-134212]
- kvm-target-i386-mshv-Integrate-x86-instruction-decoder-e.patch [RHEL-134212]
- kvm-target-i386-mshv-Write-MSRs-to-the-hypervisor.patch [RHEL-134212]
- kvm-target-i386-mshv-Implement-mshv_vcpu_run.patch [RHEL-134212]
- kvm-accel-mshv-Handle-overlapping-mem-mappings.patch [RHEL-134212]
- kvm-qapi-accel-Allow-to-query-mshv-capabilities.patch [RHEL-134212]
- kvm-target-i386-mshv-Use-preallocated-page-for-hvcall.patch [RHEL-134212]
- kvm-docs-Add-mshv-to-documentation.patch [RHEL-134212]
- kvm-MAINTAINERS-Add-maintainers-for-mshv-accelerator.patch [RHEL-134212]
- kvm-accel-mshv-initialize-thread-name.patch [RHEL-134212]
- kvm-accel-mshv-use-return-value-of-handle_pio_str_read.patch [RHEL-134212]
- Resolves: RHEL-129540
  (Assertion failure on drain with iothread and I/O load)
- Resolves: RHEL-121543
  (The VM hit io error when do S3-PR integration on the pass-through  failover multipath device)
- Resolves: RHEL-134212
  ([RHEL10.2] L1VH qemu downstream initial merge RHEL10.2)

* Mon Dec 01 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-7
- kvm-pcie_sriov-Fix-broken-MMIO-accesses-from-SR-IOV-VFs.patch [RHEL-120115]
- kvm-arm-fix-oob-access-in-compat-handling.patch [RHEL-130478]
- Resolves: RHEL-120115
  (The vf nic created using the IGB emulated nic can not obtain ip address )
- Resolves: RHEL-130478
  (Migration from RHEL 10.2 to RHEL 10.1 with virt-rhel10.0.0 machine type fails on Grace)

* Tue Nov 25 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-6
- kvm-ram-block-attributes-fix-interaction-with-hugetlb-me.patch [RHEL-126708]
- kvm-ram-block-attributes-Unify-the-retrieval-of-the-bloc.patch [RHEL-126708]
- kvm-hw-s390x-Fix-a-possible-crash-with-passed-through-vi.patch [RHEL-128085]
- kvm-Fix-the-typo-of-vfio-pci-device-s-enable-migration-o.patch [RHEL-130704]
- Resolves: RHEL-126708
  ([RHEL 10]snp guest fail to boot with hugepage)
- Resolves: RHEL-128085
  (VM crashes during boot when virtio device is attached through vfio_ccw)
- Resolves: RHEL-130704
  ([rhel10] Fix the typo under vfio-pci device's enable-migration option )

* Fri Nov 14 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-5
- kvm-io-move-websock-resource-release-to-close-method.patch [RHEL-120116]
- kvm-io-fix-use-after-free-in-websocket-handshake-code.patch [RHEL-120116]
- kvm-vfio-Disable-VFIO-migration-with-MultiFD-support.patch [RHEL-126573]
- kvm-hw-arm-virt-Use-ACPI-PCI-hotplug-by-default-from-10..patch [RHEL-67323]
- kvm-hw-arm-smmu-common-Check-SMMU-has-PCIe-Root-Complex-.patch [RHEL-73800]
- kvm-hw-arm-virt-acpi-build-Re-arrange-SMMUv3-IORT-build.patch [RHEL-73800]
- kvm-hw-arm-virt-acpi-build-Update-IORT-for-multiple-smmu.patch [RHEL-73800]
- kvm-hw-arm-virt-Factor-out-common-SMMUV3-dt-bindings-cod.patch [RHEL-73800]
- kvm-hw-arm-virt-Add-an-SMMU_IO_LEN-macro.patch [RHEL-73800]
- kvm-hw-pci-Introduce-pci_setup_iommu_per_bus-for-per-bus.patch [RHEL-73800]
- kvm-hw-arm-virt-Allow-user-creatable-SMMUv3-dev-instanti.patch [RHEL-73800]
- kvm-qemu-options.hx-Document-the-arm-smmuv3-device.patch [RHEL-73800]
- kvm-bios-tables-test-Allow-for-smmuv3-test-data.patch [RHEL-73800]
- kvm-qtest-bios-tables-test-Add-tests-for-legacy-smmuv3-a.patch [RHEL-73800]
- kvm-qtest-bios-tables-test-Update-tables-for-smmuv3-test.patch [RHEL-73800]
- kvm-qtest-Do-not-run-bios-tables-test-on-aarch64.patch []
- Resolves: RHEL-120116
  (CVE-2025-11234 qemu-kvm: VNC WebSocket handshake use-after-free [rhel-10.2])
- Resolves: RHEL-126573
  (VFIO migration using multifd should be disabled by default)
- Resolves: RHEL-67323
  ([aarch64] Support ACPI based PCI hotplug on ARM)
- Resolves: RHEL-73800
  (NVIDIA:Grace-Hopper:Backport support for user-creatable nested SMMUv3 - RHEL 10.1)

* Mon Nov 03 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-4
- kvm-qapi-machine-s390x-add-QAPI-event-SCLP_CPI_INFO_AVAI.patch [RHEL-104009 RHEL-105823 RHEL-73008]
- kvm-tests-functional-add-tests-for-SCLP-event-CPI.patch [RHEL-104009 RHEL-105823 RHEL-73008]
- kvm-redhat-Add-new-rhel9.8.0-and-rhel10.2.0-machine-type.patch [RHEL-104009 RHEL-105823 RHEL-73008]
- kvm-vfio-rename-field-to-num_initial_regions.patch [RHEL-118810]
- kvm-vfio-only-check-region-info-cache-for-initial-region.patch [RHEL-118810]
- kvm-arm-create-new-rhel-10.2-specific-virt-machine-type.patch [RHEL-105826 RHEL-105828]
- kvm-arm-create-new-rhel-9.8-specific-virt-machine-type.patch [RHEL-105826 RHEL-105828]
- kvm-x86-create-new-rhel-10.2-specific-pc-q35-machine-typ.patch [RHEL-105826 RHEL-105828]
- kvm-x86-create-new-rhel-9.8-specific-pc-q35-machine-type.patch [RHEL-105826 RHEL-105828]
- kvm-rh-enable-CONFIG_USB_STORAGE_BOT.patch [RHEL-101929]
- Resolves: RHEL-104009
  ([IBM 10.2 FEAT] KVM: Enhance machine type definition to include CPI and PCI passthru capabilities (qemu))
- Resolves: RHEL-105823
  (Add new -rhel10.2.0 machine type to qemu-kvm [s390x])
- Resolves: RHEL-73008
  ([IBM 10.2 FEAT] KVM: Implement Control Program Identification (qemu))
- Resolves: RHEL-118810
  ([RHEL 10.2] Windows 11 VM fails to boot up with ramfb='on' with QEMU 10.1)
- Resolves: RHEL-105826
  (Add new -rhel10.2.0 machine type to qemu-kvm [aarch64])
- Resolves: RHEL-105828
  (Add new -rhel10.2.0 machine type to qemu-kvm [x86_64])
- Resolves: RHEL-101929
  (enable 'usb-bot' device for proper support of USB CD-ROM drives via libvirt  )

* Mon Oct 20 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-3
- kvm-arm-kvm-report-registers-we-failed-to-set.patch [RHEL-119368]
- kvm-pcie_sriov-make-pcie_sriov_pf_exit-safe-on-non-SR-IO.patch [RHEL-116443]
- kvm-target-i386-add-compatibility-property-for-arch_capa.patch [RHEL-120253]
- kvm-target-i386-add-compatibility-property-for-pdcm-feat.patch [RHEL-120253]
- Resolves: RHEL-119368
  ([rhel10] Backport "arm/kvm: report registers we failed to set")
- Resolves: RHEL-116443
  (qemu crash after hot-unplug disk from the multifunction enabled bus,crash point PCIDevice *vf = dev->exp.sriov_pf.vf[i])
- Resolves: RHEL-120253
  (Backport fixes for PDCM and ARCH_CAPABILITIES migration incompatibility)

* Mon Sep 15 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-2
- kvm-e1000e-Prevent-crash-from-legacy-interrupt-firing-af.patch [RHEL-112882]
- Resolves: RHEL-112882
  ([DEV Task]: Assertion `core->delayed_causes == 0' failed with e1000e NIC)

* Fri Aug 29 2025 Miroslav Rezanina <mrezanin@redhat.com> - 10.1.0-1
- Rebase to QEMU 10.1.0 [RHEL-105035]
- Resolves: RHEL-105035
  (Rebase qemu-kvm to QEMU 10.1.0)

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
