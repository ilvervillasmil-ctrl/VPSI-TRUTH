"""
======================================================================
 VPSI-TRUTH  ---  modules
======================================================================

 Container root. Holds no logic and calls nothing.

 Each subdirectory is a container: it declares CONTENEDOR with its
 role and exposes what that role requires. core/engine walks this
 directory, reads the declarations, and calls by role. It never sees
 what lives inside a container.

 Dropping a container in here is enough. Nothing above needs editing.

======================================================================
"""

