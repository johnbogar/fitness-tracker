import { useState } from 'react';

function DeleteGoal(props) {
    /*
    Component to delete a goal
    Parameters: proerty for goal-id is a number
    returns: nothing
    */

    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
        // send response
        const response = await fetch('http://localhost:5000/api/delete_goal', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goalId:props.goalId
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete goal');
        }

        setSuccess('Goal deleted successfully!');
        setError('');

        props.onGoalDeleted();
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
                        className="delete-goal-form"
                        onSubmit={handleSubmit}
                    >
                        <h2 className="form-title">Delete Goal</h2>

                        {error && (
                            <p className="error-message">{error}</p>
                        )}
                        <h3>Are you sure you want to delete this goal?</h3>

                        <div className="form-buttons">
                            <button
                                type="submit"
                                className="submit-btn"
                            >
                                Delete Permanently 
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

export default DeleteGoal;