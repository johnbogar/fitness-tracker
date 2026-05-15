import { useState, useEffect } from 'react';

function EditGoal(props) {
    /*
    Component to edit a goal
    Parameters: proerty for goal-id is a number
    returns: nothing
    */

    //variables for inputs
    const [goalName, setGoalName] = useState(props.goalName || '');
    const [goalDesc, setGoalDesc] = useState(props.goalDesc || '');
    const [endDate, setEndDate] = useState(props.endDate || '');
    const [estimatedWorkouts, setEstimatedWorkouts] = useState(props.estimatedWorkouts || 10);

    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        setGoalName(props.goalName || '');
        setGoalDesc(props.goalDesc || '');
        setEndDate(props.endDate || '');
        setEstimatedWorkouts(props.estimatedWorkouts || 10);
    }, [props.goalId]);

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // validate inputs
    if (!goalName.trim()) {
        setError('Goal name is required');
        return;
    }

    if (goalName.length > 255 || goalDesc.length > 255) {
        setError('Fields must be under 255 characters');
        return;
    }

    const estNum = parseInt(estimatedWorkouts, 10);
    if (isNaN(estNum) || estNum < 1) {
        setError('Estimated workouts must be a positive number');
        return;
    }

    try {
        // send response
        const response = await fetch('http://localhost:5000/api/edit_goal', {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goalId: props.goalId,
                goalName,
                goalDesc,
                endDate,
                estimatedWorkouts: parseInt(estimatedWorkouts, 10)
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to edit goal');
        }

        setSuccess('Goal edited successfully!');
        setError('');

        props.onGoalUpdated();
    } catch (err) {
        setError(err.message);
    }
    };

    return (
        <>
            <div className="modal-overlay">
                <div className="modal">
                    {success && (
                        <>
                            <p className="success-message">{success}</p>
                            <button className="close-btn" onClick={props.onClose}>Close</button>
                        </>
                    )}
                    {!success && (<form
                        className="edit-goal-form"
                        onSubmit={handleSubmit}
                    >
                    
                    <h2 className="form-title">Edit Goal</h2>

                        {error && (
                            <p className="error-message">{error}</p>
                        )}
                        <label
                            htmlFor="goalName"
                            className="form-label"
                        >
                            Goal Name
                        </label>
                        <input
                            id="goalName"
                            className="form-input"
                            type="text"
                            value={goalName}
                            onChange={(e) => setGoalName(e.target.value)}
                        />

                        <label
                            htmlFor="goalDesc"
                            className="form-label"
                        >
                            Description
                        </label>
                        <textarea
                            id="goalDesc"
                            className="form-text"
                            value={goalDesc}
                            onChange={(e) => setGoalDesc(e.target.value)}
                        />

                        <label
                            htmlFor="endDate"
                            className="form-label"
                        >
                            End Date
                        </label>
                        <input
                            id="endDate"
                            className="form-input"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />

                        <label
                            htmlFor="estimatedWorkouts"
                            className="form-label"
                        >
                            Estimated Workouts
                        </label>
                        <input
                            id="estimatedWorkouts"
                            className="form-input"
                            type="number"
                            min="1"
                            value={estimatedWorkouts}
                            onChange={(e) => setEstimatedWorkouts(e.target.value)}
                        />

                        <div className="form-buttons">
                            <button
                                type="submit"
                                className="submit-btn"
                            >
                                Update
                            </button>

                            <button
                                type="button"
                                className="close-btn"
                                onClick={props.onClose}
                            >
                                Close
                            </button>
                        </div>
                    </form>
                    )}
                </div>
            </div>
        </>
  );
}

export default EditGoal;