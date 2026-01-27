import React, { useState, useEffect } from 'react';
import { Calendar, CheckSquare, X, Plus, List, Grid } from 'lucide-react';

const CalendarTodoPanel = ({ socket, position, onClose, onMouseDown, activeDragElement, zIndex }) => {
    const [calendarEvents, setCalendarEvents] = useState([]);
    const [todos, setTodos] = useState([]);
    const [newTodo, setNewTodo] = useState('');
    const [loading, setLoading] = useState(false);
    const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'
    const [currentMonth, setCurrentMonth] = useState(new Date());

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
            console.log('[CALENDAR] Received events:', events);
            
            if (!events || events.length === 0) {
                console.log('[CALENDAR] No events received');
                setCalendarEvents([]);
                return;
            }
            
            // Format events for display - preserve original date format for calendar view
            const formattedEvents = events.map(event => {
                // Try to parse the date - handle both ISO strings and formatted dates
                let eventDate;
                try {
                    if (event.date) {
                        // Try parsing as YYYY-MM-DD first
                        eventDate = new Date(event.date + 'T00:00:00');
                        // If date is invalid, try parsing as-is
                        if (isNaN(eventDate.getTime())) {
                            eventDate = new Date(event.date);
                        }
                        // If still invalid, use today
                        if (isNaN(eventDate.getTime())) {
                            eventDate = new Date();
                        }
                    } else {
                        eventDate = new Date();
                    }
                } catch {
                    eventDate = new Date();
                }
                
                return {
                    id: event.id || Date.now() + Math.random(),
                    title: event.title || 'Untitled Event',
                    time: event.time || eventDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    date: eventDate.toISOString().split('T')[0], // Store as YYYY-MM-DD for calendar view
                    dateDisplay: eventDate.toLocaleDateString(), // For display in list view
                    description: event.description || ''
                };
            });
            
            console.log('[CALENDAR] Formatted events:', formattedEvents);
            setCalendarEvents(formattedEvents);
            // Also send to backend for agent cache
            socket.emit('calendar_events_list', { events: formattedEvents });
        };
        
        // Handle todos list from backend (from external API)
        const handleTodosList = (data) => {
            console.log('[TODOS] Received todos list from backend:', data);
            if (data && data.todos && Array.isArray(data.todos)) {
                // Update local state with todos from API
                setTodos(data.todos);
                // Also save to localStorage
                localStorage.setItem('jarvis_todos', JSON.stringify(data.todos));
            }
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
        socket.on('todos_list', handleTodosList); // Handle todos from backend API

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

    // Calendar view helpers
    const getDaysInMonth = (date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        return new Date(year, month + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        return new Date(year, month, 1).getDay();
    };

    const getEventsForDate = (date) => {
        const dateStr = date.toISOString().split('T')[0];
        return calendarEvents.filter(event => {
            const eventDate = new Date(event.date);
            return eventDate.toISOString().split('T')[0] === dateStr;
        });
    };

    const formatDateForEvent = (dateStr) => {
        try {
            const date = new Date(dateStr);
            return date.toISOString().split('T')[0];
        } catch {
            return new Date().toISOString().split('T')[0];
        }
    };

    const renderCalendarView = () => {
        const daysInMonth = getDaysInMonth(currentMonth);
        const firstDay = getFirstDayOfMonth(currentMonth);
        const days = [];
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December'];
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDay; i++) {
            days.push(null);
        }
        
        // Add cells for each day of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
            const eventsForDay = getEventsForDate(date);
            days.push({ day, date, events: eventsForDay });
        }
        
        return (
            <div className="flex flex-col h-full">
                {/* Month Navigation */}
                <div className="flex items-center justify-between mb-2 px-1">
                    <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                        className="text-cyan-400 hover:text-cyan-300 text-xs px-2 py-1 rounded"
                    >
                        ←
                    </button>
                    <span className="text-xs font-semibold text-cyan-300">
                        {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                    </span>
                    <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                        className="text-cyan-400 hover:text-cyan-300 text-xs px-2 py-1 rounded"
                    >
                        →
                    </button>
                </div>
                
                {/* Calendar Grid */}
                <div className="flex-1 overflow-y-auto">
                    {/* Day headers */}
                    <div className="grid grid-cols-7 gap-1 mb-1">
                        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                            <div key={day} className="text-[9px] text-gray-500 text-center font-mono py-1">
                                {day}
                            </div>
                        ))}
                    </div>
                    
                    {/* Calendar days */}
                    <div className="grid grid-cols-7 gap-1">
                        {days.map((dayData, idx) => {
                            if (dayData === null) {
                                return <div key={`empty-${idx}`} className="aspect-square"></div>;
                            }
                            
                            const isToday = dayData.date.toDateString() === new Date().toDateString();
                            const hasEvents = dayData.events.length > 0;
                            
                            return (
                                <div
                                    key={dayData.day}
                                    className={`aspect-square border rounded p-1 text-[10px] ${
                                        isToday 
                                            ? 'border-cyan-500 bg-cyan-500/20' 
                                            : hasEvents 
                                                ? 'border-cyan-500/30 bg-gray-900/30' 
                                                : 'border-gray-700 bg-gray-900/10'
                                    }`}
                                >
                                    <div className={`font-mono ${isToday ? 'text-cyan-300 font-bold' : 'text-gray-400'}`}>
                                        {dayData.day}
                                    </div>
                                    {hasEvents && (
                                        <div className="mt-0.5 space-y-0.5">
                                            {dayData.events.slice(0, 2).map(event => (
                                                <div
                                                    key={event.id}
                                                    className="bg-cyan-500/30 rounded px-1 py-0.5 text-[8px] text-cyan-200 truncate"
                                                    title={event.title}
                                                >
                                                    {event.title}
                                                </div>
                                            ))}
                                            {dayData.events.length > 2 && (
                                                <div className="text-[8px] text-cyan-400 text-center">
                                                    +{dayData.events.length - 2}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        );
    };

    const renderListView = () => {
        return (
            <div className="space-y-2 overflow-y-auto h-full">
                {calendarEvents.length === 0 ? (
                    <div className="text-gray-600 text-xs font-mono py-4 text-center">
                        No events scheduled
                    </div>
                ) : (
                    calendarEvents.map(event => (
                        <div key={event.id} className="bg-gray-900/50 border border-cyan-500/20 rounded p-2 text-xs">
                            <div className="text-cyan-300 font-semibold">{event.title}</div>
                            <div className="text-gray-500 text-[10px] mt-1">
                                {event.time} • {event.dateDisplay || event.date}
                            </div>
                        </div>
                    ))
                )}
            </div>
        );
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
                <div className="flex-1 border-b border-gray-800 overflow-hidden p-3 flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xs font-bold text-cyan-400 flex items-center gap-1">
                            <Calendar size={12} />
                            {viewMode === 'list' ? "TODAY'S EVENTS" : "CALENDAR"}
                        </h3>
                        <div className="flex gap-1">
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-1 rounded transition-colors ${
                                    viewMode === 'list' 
                                        ? 'bg-cyan-500/30 text-cyan-300' 
                                        : 'text-gray-500 hover:text-gray-400'
                                }`}
                                title="List View"
                            >
                                <List size={12} />
                            </button>
                            <button
                                onClick={() => setViewMode('calendar')}
                                className={`p-1 rounded transition-colors ${
                                    viewMode === 'calendar' 
                                        ? 'bg-cyan-500/30 text-cyan-300' 
                                        : 'text-gray-500 hover:text-gray-400'
                                }`}
                                title="Calendar View"
                            >
                                <Grid size={12} />
                            </button>
                        </div>
                    </div>
                    <div className="flex-1 overflow-hidden">
                        {viewMode === 'calendar' ? renderCalendarView() : renderListView()}
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
