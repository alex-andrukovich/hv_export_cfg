# hv_export_cfg
Maps the following via CCI, each is represented with a tab in an Excel format:\
Summary_storage-serial;\
Snapshots;\
Journals;\
Journal_MUs;\
RCUs;\
Licenses;\
Pools;\
Quorum;\
Ports;\
HORCM file that is used for replication mapping;\
Replication_remote;\
Replication_local;\
Luns;\
Hba_wwns;\
Ldevs_mapped;\
Ldevs_defined;\
Ldevs_unmapped (doesn't work on simulators, therefore ### in the code);\
Host_groups;\
\
\
Argument Example: -s 10.0.0.118 -u maintenance -p raid-maintenance -i 999 -n 44666
\
\
add c:\horcm\etc to path before using
must be admin or have write permissions to C:\HORCM\usr\var for cached credentials to be created (raidcom login process)
