import React, {useEffect, useState} from "react";
import axios from "axios";
import GoalItem from '../components/GoalItem'
import AddGoal from '../components/AddGoal'
import DeleteGoal from "../components/DeleteGoal";
import EditGoal from "../components/EditGoal";
import '../styles/goals.css';

export default function ViewGoals()
/*
Component for view goals page
*/
{
    const [goals, setGoals] = useState([]);
    const [selectedGoal, setSelectedGoal] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);

    // access api and get the goals
    const fetchGoals = () => {
        axios.get("http://localhost:5000/api/view_goals", {
            withCredentials: true
        })
        .then(res => setGoals(res.data))
        .catch(err => console.error(err));
    }
    useEffect(() => {
        fetchGoals();
    }, []);

    return (
        <>
            <div className="view-goals">
                <div className="goals-card">
                <h1 className="goals-title">Your goals</h1>

                <div className="goals">
                     {goals.length === 0 ? (
                        <div className="empty-state">
                            <h3>No goals yet</h3>
                            <p>Add a goal to start your progress 🚀</p>
                        </div>
                    ) : goals.map((goal) => {
                        return (
                            <GoalItem 
                                key={goal.id}
                                id={goal.id}
                                goalName={goal.goalname}
                                goalDesc={goal.goaldesc}
                                onDeleteClick={() => {
                                    setSelectedGoal(goal);
                                    setShowDeleteModal(true);
                                }}
                                onUpdateClick={() => {
                                    setSelectedGoal(goal);
                                    setShowEditModal(true);
                                }}
                            />
                        );
                    })}
                </div>
                </div>

                <AddGoal 
                    userId={1}
                    onGoalAdded={fetchGoals}
                />
                {showDeleteModal && (
                <DeleteGoal
                    goalId={selectedGoal.id}
                    onClose={() => setShowDeleteModal(false)}
                    onGoalDeleted={() => {
                        fetchGoals();
                        setTimeout(() => {
                            setShowDeleteModal(false);
                        }, 800);
                    }}
                />
                )}
                {showEditModal && (
                <EditGoal
                    goalId={selectedGoal.id}
                    goalName={selectedGoal.goalname}
                    goalDesc={selectedGoal.goaldesc}
                    endDate={selectedGoal.enddate}
                    estimatedWorkouts={selectedGoal.estimated_workouts ?? 10}
                    onClose={() => setShowEditModal(false)}
                    onGoalUpdated={() => {
                        fetchGoals();
                        setTimeout(() => {
                            setShowEditModal(false);
                        }, 800);
                    }}
                />
                )}
            </div>
        </>
    );
}