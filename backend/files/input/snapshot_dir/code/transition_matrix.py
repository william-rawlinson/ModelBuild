import numpy as np
from math import exp

def get_transition_matrix(context: TransitionMatrixContext) -> np.ndarray:
    """
    Generate transition matrix for a cohort Markov model comparing VBT to spinal fusion.
    
    Args:
        context: Contains health states, cycle number, treatment arm, and parameters
        
    Returns:
        Transition probability matrix as numpy array
    """
    # Initialize transition matrix with named states
    transition_matrix = NamedTransitionMatrix(context.health_states)
    
    # Extract parameters
    params = context.params
    cycle = context.cycle
    
    # Determine if we're in the first cycle (cycle 0)
    is_first_cycle = (cycle == 0)
    
    # 1. Transitions from Spinal Fusion Index Procedure
    transition_matrix.set("Spinal Fusion Index Procedure", "Postoperative Fusion", 1.0)
    
    # 2. Transitions from VBT Index Procedure
    transition_matrix.set("VBT Index Procedure", "Postoperative VBT", 1.0)
    
    # 3. Transitions from Postoperative VBT
    # Use different probabilities for first cycle vs. later cycles
    vbt_to_fusion_prob = params["vbt_to_fusion_prob_q1"] if is_first_cycle else params["vbt_to_fusion_prob_later"]
    
    transition_matrix.set("Postoperative VBT", "VBT Revision", params["vbt_revision_prob_quarterly"])
    transition_matrix.set("Postoperative VBT", "Spinal Fusion Index Procedure", vbt_to_fusion_prob)
    transition_matrix.set("Postoperative VBT", "Postoperative VBT", 
                         1.0 - params["vbt_revision_prob_quarterly"] - vbt_to_fusion_prob)
    
    # 4. Transitions from Postoperative Fusion
    fusion_revision_prob = params["fusion_revision_prob_q1"] if is_first_cycle else params["fusion_revision_prob_later"]
    
    transition_matrix.set("Postoperative Fusion", "Fusion Revision 1", fusion_revision_prob)
    transition_matrix.set("Postoperative Fusion", "Postoperative Fusion", 1.0 - fusion_revision_prob)
    
    # 5. Transitions from VBT Revision
    transition_matrix.set("VBT Revision", "Postoperative VBT", 1.0)
    
    # 6. Transitions from Fusion Revision 1
    transition_matrix.set("Fusion Revision 1", "Postoperative Fusion Revision 1", 1.0)
    
    # 7. Transitions from Postoperative Fusion Revision 1
    fusion_revision_prob = params["fusion_revision_prob_q1"] if is_first_cycle else params["fusion_revision_prob_later"]
    
    transition_matrix.set("Postoperative Fusion Revision 1", "Fusion Revision 2", fusion_revision_prob)
    transition_matrix.set("Postoperative Fusion Revision 1", "Postoperative Fusion Revision 1", 
                         1.0 - fusion_revision_prob)
    
    # 8. Transitions from Fusion Revision 2
    transition_matrix.set("Fusion Revision 2", "Postoperative Fusion Revision 2", 1.0)
    
    # 9. Transitions from Postoperative Fusion Revision 2
    fusion_revision_prob = params["fusion_revision_prob_q1"] if is_first_cycle else params["fusion_revision_prob_later"]
    
    transition_matrix.set("Postoperative Fusion Revision 2", "Ineligible For Further Fusion Revision", fusion_revision_prob)
    transition_matrix.set("Postoperative Fusion Revision 2", "Postoperative Fusion Revision 2", 
                         1.0 - fusion_revision_prob)
    
    # 10. Transitions from Ineligible For Further Fusion Revision (absorbing state)
    transition_matrix.set("Ineligible For Further Fusion Revision", "Ineligible For Further Fusion Revision", 1.0)
    
    # Return the transition matrix as a numpy array
    return transition_matrix.as_array()