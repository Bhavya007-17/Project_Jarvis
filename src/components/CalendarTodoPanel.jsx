import React, { useState, useEffect } from 'react';
import { Calendar, CheckSquare, X, Plus } from 'lucide-react';

const CalendarTodoPanel = ({ socket, position, onClose, onMouseDown, activeDragElement, zIndex }) => {
    const [calendarEvents, setCalendarEvents] = useState([]);
    const [todos, setTodos] = useState([]);
    const [newTodo, setNewTodo] = useState('');
    const [loading, setLoading] = useState(false);

    // Load todos from localStorage on mount
    useEffect(() => {
        const savedTodos = localStorage.getItem('jarvis_todos');
        if (savedTodos) {
            try {
                setTodos(JSON.parse(savedTodos));
            } catch (e) {
                console.error('Error loading todos:', e);
            }
        }
    }, []);

    // Save todos to localStorage and sync with backend whenever they change
    useEffect(() => {
        localStorage.setItem('jarvis_todos', JSON.stringify(todos));
        // Sync with backend
        if (socket && socket.connected) {
            socket.emit('todos_list', { todos: todos });
        }
    }, [todos, socket]);

    // Fetch Google Calendar events
    useEffect(() => {
        const fetchCalendarEvents = async () => {
            setLoading(true);
            try {
                // Request calendar events from backend
                socket.emit('get_calendar_events');
            } catch (error) {
                console.error('Error fetching calendar events:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchCalendarEvents();

        // Set up socket listener for calendar events
        const handleCalendarEvents = (events) => {
            // Format events for display
            const formattedEvents = events.map(event => ({
                id: event.id,
                title: event.title,
                time: event.time || new Date(event.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                date: event.date ? new Date(event.date).toLocaleDateString() : new Date().toLocaleDateString(),
                description: event.description || ''
            }));
            setCalendarEvents(formattedEvents);
            // Also send to backend for agent cache
            socket.emit('calendar_events_list', { events: formattedEvents });
        };
        
        // Also send todos list on mount/update
        const sendTodosToBackend = () => {
            const savedTodos = localStorage.getItem('jarvis_todos');
            if (savedTodos) {
                try {
                    const todosData = JSON.parse(savedTodos);
                    socket.emit('todos_list', { todos: todosData });
                } catch (e) {
                    console.error('Error sending todos:', e);
                }
            }
        };
        
        // Send todos on mount
        sendTodosToBackend();

        // Handle todo updates from agent
        const handleTodoUpdate = (data) => {
            console.log('Todo update received:', data);
            setTodos(currentTodos => {
                let updatedTodos;
                if (data.action === 'add' && data.task) {
                    const todo = {
                        id: Date.now(),
                        text: data.task,
                        completed: false,
                        createdAt: new Date().toISOString()
                    };
                    updatedTodos = [...currentTodos, todo];
                    localStorage.setItem('jarvis_todos', JSON.stringify(updatedTodos));
                } else if (data.action === 'complete' && data.task_id) {
                    updatedTodos = currentTodos.map(todo => 
                        todo.id === data.task_id ? { ...todo, completed: true } : todo
                    );
                    localStorage.setItem('jarvis_todos', JSON.stringify(updatedTodos));
                } else if (data.action === 'delete' && data.task_id) {
                    updatedTodos = currentTodos.filter(todo => todo.id !== data.task_id);
                    localStorage.setItem('jarvis_todos', JSON.stringify(updatedTodos));
            } else if (data.action === 'get') {
                // Send current todos list to backend immediately
                socket.emit('todos_list', { todos: currentTodos });
                return currentTodos;
                } else {
                    return currentTodos;
                }
                return updatedTodos;
            });
        };

        // Handle calendar updates from agent
        const handleCalendarUpdate = (data) => {
            console.log('Calendar update received:', data);
            setCalendarEvents(currentEvents => {
                if (data.action === 'add') {
                    const newEvent = {
                        id: Date.now(),
                        title: data.title,
                        time: data.time,
                        date: data.date || new Date().toISOString().split('T')[0],
                        description: data.description || ''
                    };
                    return [...currentEvents, newEvent];
                } else if (data.action === 'get') {
                    // Calendar events are already fetched via get_calendar_events
                    fetchCalendarEvents();
                    // Send current events to backend
                    socket.emit('calendar_events_list', { events: currentEvents });
                    return currentEvents;
                }
                return currentEvents;
            });
        };

        // Handle request for todos list
        const handleRequestTodos = () => {
            setTodos(currentTodos => {
                socket.emit('todos_list', { todos: currentTodos });
                return currentTodos;
            });
        };

        socket.on('calendar_events', handleCalendarEvents);
        socket.on('todo_update', handleTodoUpdate);
        socket.on('calendar_update', handleCalendarUpdate);
        socket.on('request_todos', handleRequestTodos);

        // Refresh events every 5 minutes
        const interval = setInterval(fetchCalendarEvents, 5 * 60 * 1000);

        return () => {
            socket.off('calendar_events', handleCalendarEvents);
            socket.off('todo_update', handleTodoUpdate);
            socket.off('calendar_update', handleCalendarUpdate);
            socket.off('request_todos', handleRequestTodos);
            clearInterval(interval);
        };
    }, [socket]);

    const addTodo = () => {
        if (newTodo.trim()) {
            const todo = {
                id: Date.now(),
                text: newTodo.trim(),
                completed: false,
                createdAt: new Date().toISOString()
            };
            setTodos([...todos, todo]);
            setNewTodo('');
        }
    };

    const toggleTodo = (id) => {
        setTodos(todos.map(todo => 
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        ));
    };

    const deleteTodo = (id) => {
        setTodos(todos.filter(todo => todo.id !== id));
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            addTodo();
        }
    };

    return (
        <div
            className={`absolute flex flex-col transition-all duration-200 
                backdrop-blur-xl bg-black/40 border border-white/10 shadow-2xl overflow-hidden rounded-lg
                ${activeDragElement === 'calendar' ? 'ring-2 ring-green-500 bg-green-500/10' : ''}
            `}
            style={{
                left: position?.x || window.innerWidth / 2,
                top: position?.y || window.innerHeight / 2,
                transform: 'translate(-50%, -50%)',
                width: '450px',
                height: '600px',
                pointerEvents: 'auto',
                zIndex: zIndex || 30
            }}
            onMouseDown={onMouseDown}
        >
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none mix-blend-overlay z-10"></div>
            
            {/* Header */}
            <div data-drag-handle className="h-10 bg-[#222] border-b border-gray-700 flex items-center justify-between px-3 shrink-0 cursor-grab active:cursor-grabbing">
                <div className="flex items-center gap-2 text-gray-300 text-xs font-mono">
                    <Calendar size={14} className="text-cyan-500" />
                    <span>CALENDAR & TODOS</span>
                </div>
                <button onClick={onClose} className="hover:bg-red-500/20 text-gray-400 hover:text-red-400 p-1 rounded transition-colors">
                    <X size={14} />
                </button>
            </div>

            <div className="relative z-20 flex-1 flex flex-col overflow-hidden">
                {/* Calendar Section */}
                <div className="flex-1 border-b border-gray-800 overflow-y-auto p-3">
                    <h3 className="text-xs font-bold text-cyan-400 mb-2 flex items-center gap-1">
                        <Calendar size={12} />
                        TODAY'S EVENTS
                    </h3>
                    <div className="space-y-2">
                        {calendarEvents.length === 0 ? (
                            <div className="text-gray-600 text-xs font-mono py-4 text-center">
                                No events scheduled
                            </div>
                        ) : (
                            calendarEvents.map(event => (
                                <div key={event.id} className="bg-gray-900/50 border border-cyan-500/20 rounded p-2 text-xs">
                                    <div className="text-cyan-300 font-semibold">{event.title}</div>
                                    <div className="text-gray-500 text-[10px] mt-1">{event.time} • {event.date}</div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Todo Section */}
                <div className="flex-1 overflow-y-auto p-3">
                    <h3 className="text-xs font-bold text-cyan-400 mb-2 flex items-center gap-1">
                        <CheckSquare size={12} />
                        TODO LIST
                    </h3>
                    
                    {/* Add Todo Input */}
                    <div className="flex gap-2 mb-3">
                        <input
                            type="text"
                            value={newTodo}
                            onChange={(e) => setNewTodo(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Add new todo..."
                            className="flex-1 bg-gray-900/50 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-cyan-500"
                        />
                        <button
                            onClick={addTodo}
                            className="bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 rounded px-2 py-1 text-cyan-400 transition-colors"
                        >
                            <Plus size={14} />
                        </button>
                    </div>

                    {/* Todo List */}
                    <div className="space-y-2">
                        {todos.length === 0 ? (
                            <div className="text-gray-600 text-xs font-mono py-4 text-center">
                                No todos yet. Add one above!
                            </div>
                        ) : (
                            todos.map(todo => (
                                <div
                                    key={todo.id}
                                    className={`flex items-center gap-2 bg-gray-900/50 border rounded p-2 ${
                                        todo.completed 
                                            ? 'border-gray-700 opacity-60' 
                                            : 'border-cyan-500/20'
                                    }`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={todo.completed}
                                        onChange={() => toggleTodo(todo.id)}
                                        className="w-3 h-3 text-cyan-500 rounded focus:ring-cyan-500"
                                    />
                                    <span
                                        className={`flex-1 text-xs ${
                                            todo.completed 
                                                ? 'line-through text-gray-600' 
                                                : 'text-gray-300'
                                        }`}
                                    >
                                        {todo.text}
                                    </span>
                                    <button
                                        onClick={() => deleteTodo(todo.id)}
                                        className="text-gray-500 hover:text-red-400 transition-colors"
                                    >
                                        <X size={12} />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CalendarTodoPanel;
