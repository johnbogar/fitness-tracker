import { useState } from 'react';

function AddGoal(props) {
    /*
    Component to aadd a goal
    Parameters: proerty for user-id is a number
    returns: nothing
    */

    //variables for inputs
    const [goalName, setGoalName] = useState('');
    const [goalDesc, setGoalDesc] = useState('');
    const [endDate, setEndDate] = useState('');
    const [estimatedWorkouts, setEstimatedWorkouts] = useState(10);

    const [show, setShow] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleClose = () => {
        setShow(false);
        setError('');
    }
    const handleShow = () => {
        setShow(true);
        setSuccess('');
        setError('');
    };

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // validate inputs
    if (!goalName.trim()) {
        setError('Goal name is required');
        return;
    }

    if (!props.userId) {
        setError('User not found');
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
        const response = await fetch('http://localhost:5000/api/add_goal', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goalName,
                goalDesc,
                userId: props.userId,
                endDate,
                estimatedWorkouts: parseInt(estimatedWorkouts, 10)
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to add goal');
        }

        setSuccess('Goal added successfully!');
        setError('');

        setGoalName('');
        setGoalDesc('');
        setEndDate('');
        setEstimatedWorkouts(10);

        if (props.onGoalAdded) {
            props.onGoalAdded(data);
        }

    } catch (err) {
        setError(err.message);
    }
    };

    return (
        <>
            <button className="add-goal-btn" onClick={handleShow}>
                Add Goal
            </button>
            {show && (
                <div className="modal-overlay">
                    <div className="modal">
                        {success && (
                            <>
                                <p className="success-message">{success}</p>
                                <button className="close-btn" onClick={handleClose}>Close</button>
                            </>
                        )}
                        {!success && (<form
                            className="add-goal-form"
                            onSubmit={handleSubmit}
                        >
                            <h2 className="form-title">Add Goal</h2>

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
                                    Submit
                                </button>

                                <button
                                    type="button"
                                    className="close-btn"
                                    onClick={handleClose}
                                >
                                    Close
                                </button>
                            </div>
                        </form>
                        )}
                    </div>
                </div>
            )}
        
        </>
  );
}

export default AddGoal;