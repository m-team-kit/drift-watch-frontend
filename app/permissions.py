# permissions.py

from typing import List, Dict

class PermissionManager:
    """
    Class to manage user permissions for accessing experiments.

    This class determines whether a user has access to a specific experiment based on their entitlements and
    user ID. The permission rules are as follows:
    - If an experiment is public, it is accessible to everyone.
    - If the user's ID is explicitly listed in the experiment's permissions, they are granted access.
    - If the user has any entitlement that matches the experiment's permission, they are granted access.
    """

    def __init__(self, user_id: str, entitlements: List[str], experiments: List[Dict]):
        """
        Initializes the PermissionManager with user-specific details.

        Args:
            user_id (str): The unique identifier of the user.
            entitlements (List[str]): A list of entitlements assigned to the user.
            experiments (List[Dict]): A list of experiments, each represented as a dictionary containing
                experiment details, such as its ID, permissions, and whether it is public.
        """
        self.user_id = user_id
        self.entitlements = entitlements
        self.experiments = experiments
        self.permissions = self._compute_permissions()  # Precompute access rights for experiments

    def _compute_permissions(self) -> Dict[str, bool]:
        """
        Computes which experiments the user has access to.

        The access is determined based on:
        - If the experiment is public, it is accessible to everyone.
        - If the user ID is explicitly mentioned in the permissions, the user has access.
        - If the user has any entitlement that matches the experiment's permission, the user has access.

        Returns:
            Dict[str, bool]: A dictionary with experiment IDs as keys and boolean values indicating access.
        """
        permissions = {}

        if self.experiments:
            for exp in self.experiments:  
                exp_id = exp["id"]
                is_public = exp["public"]
                exp_permissions = exp.get("permissions", {})
                
                # Default to allowing access if the experiment is public
                has_permission = is_public

                # Check if the user ID is explicitly allowed in experiment permissions
                if not has_permission:
                    if self.user_id in exp_permissions:
                        has_permission = True

                # Check entitlements if permission is still not granted
                if not has_permission and self.entitlements:
                    # Check if any of the user's entitlements matches the experiment permissions
                    for entitlement in self.entitlements:
                        if entitlement in exp_permissions.keys():
                            has_permission = True
                            break  # Exit loop on first matching entitlement

                permissions[exp_id] = has_permission  # Set permission status for the current experiment

        return permissions

    def has_access(self, experiment_id: str) -> bool:
        """
        Checks if the user has access to a specific experiment.

        Args:
            experiment_id (str): The unique identifier of the experiment to check access for.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        return self.permissions.get(experiment_id, False)
