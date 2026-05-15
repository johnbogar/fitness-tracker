
export default function GoalItem(properties) {
    /**
     * React component that creates a goal item 
     * params: key, id : integers, goalName, goalDesc : strings, react components for 
     * returns a div goal item with  the goals name, description, and edit and delete buttons
     **/

    return(
        <>
            <div className="goal-item">
            <h2>{properties.goalName}</h2>
            <p>{properties.goalDesc}</p>
                <div className="goal-actions">
                    <button 
                        className="delete-btn"
                        onClick={properties.onDeleteClick}
                    >
                        Delete Goal
                    </button>
                    <button 
                        className="edit-btn"
                        onClick={properties.onUpdateClick}
                    >
                        Edit Goal
                    </button>
                </div>
            </div>
        </>
    );
}