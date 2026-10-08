export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ResearchSource {
  agent_name: string;
  title: string;
  source_type?: "RAG KNOWLEDGE" | "LIVE API DATA" | "WEB RESEARCH" | "ESTIMATED INFORMATION" | string;
  url?: string;
  snippet?: string;
}

export interface FlightOption {
  airline: string;
  flight_number?: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time?: string;
  arrival_time?: string;
  duration_hours?: number;
  stops: number;
  estimated_price?: number;
  is_live_data: boolean;
  notes?: string;
}

export interface FlightResearch {
  origin_airport?: string;
  destination_airport?: string;
  route_summary?: string;
  direct_options: FlightOption[];
  connecting_options: FlightOption[];
  airlines: string[];
  fare_range_low?: number;
  fare_range_high?: number;
  estimated_duration_hours?: number;
  currency: string;
  is_live_data: boolean;
  api_status_note?: string;
  source_citations: ResearchSource[];
}

export interface HotelItem {
  name: string;
  area: string;
  approx_price_per_night: number;
  currency: string;
  rating?: number;
  description: string;
  source?: string;
  recommendation_reason?: string;
  amenities: string[];
}

export interface HotelResearch {
  recommendations: HotelItem[];
  budget_category?: string;
  avg_nightly_price?: number;
  currency: string;
  is_live_data: boolean;
  api_status_note?: string;
  source_citations: ResearchSource[];
}

export interface AttractionItem {
  name: string;
  category: string;
  description: string;
  approx_visit_time_hours: number;
  opening_hours?: string;
  entry_fee?: number;
  tips?: string;
  source?: string;
}

export interface DestinationResearch {
  major_attractions: AttractionItem[];
  cultural_sites: AttractionItem[];
  lesser_known_gems: AttractionItem[];
  neighborhoods: Array<{ name: string; vibe: string; highlights: string }>;
  local_tips: string[];
  practical_info: {
    transit_pass_recommendation?: string;
    sim_card_advice?: string;
    emergency_number?: string;
    best_way_to_commute?: string;
    [key: string]: any;
  };
  source_citations: ResearchSource[];
}

export interface WeatherResearch {
  destination: string;
  season_summary?: string;
  avg_temp_min?: number;
  avg_temp_max?: number;
  precipitation_probability?: number;
  weather_conditions?: string;
  travel_advice?: string;
  packing_suggestions: string[];
  is_live_forecast: boolean;
  api_status_note?: string;
}

export interface FoodSpotItem {
  name: string;
  area: string;
  specialty: string;
  price_level: string;
  dietary_suitability: string[];
  description?: string;
  source?: string;
}

export interface FoodResearch {
  local_dishes: Array<{
    name: string;
    description: string;
    typical_ingredients?: string;
    must_try_reason?: string;
  }>;
  popular_food_areas: string[];
  recommended_spots: FoodSpotItem[];
  street_food: Array<{
    item_name: string;
    where_to_find: string;
    approx_cost_estimate: string;
  }>;
  dietary_suitability: Record<string, string>;
  price_level_summary?: string;
  source_citations: ResearchSource[];
}

export interface ActivityItem {
  rank: number;
  title: string;
  category: string;
  description: string;
  estimated_duration_hours: number;
  estimated_cost: number;
  best_time_of_day?: string;
  source?: string;
}

export interface ActivityResearch {
  ranked_activities: ActivityItem[];
  source_citations: ResearchSource[];
}

export interface BudgetCategoryDetails {
  amount: number;
  percentage: number;
  notes?: string;
}

export interface Budget {
  id?: number;
  trip_id: number;
  flights_cost: number;
  accommodation_cost: number;
  food_cost: number;
  local_transport_cost: number;
  activities_cost: number;
  misc_cost: number;
  emergency_buffer: number;
  subtotal: number;
  total_budget: number;
  per_person_cost: number;
  currency: string;
  is_estimate: boolean;
  category_breakdown: Record<string, BudgetCategoryDetails>;
  budget_advice?: string;
}

export interface TimeBlock {
  time?: string;
  activity?: string;
  location?: string;
  transport?: string;
  estimated_cost?: number;
  practical_tip?: string;
  source?: string;
}

export interface ItineraryDay {
  id?: number;
  day_number: number;
  date_str?: string;
  theme: string;
  morning: TimeBlock;
  afternoon: TimeBlock;
  evening: TimeBlock;
  attractions: string[];
  food_suggestions: string[];
  transport_notes?: string;
  estimated_daily_spend: number;
  practical_notes?: string;
}

export interface Itinerary {
  id?: number;
  trip_id: number;
  total_days: number;
  title?: string;
  overview?: string;
  validation_status: string;
  critique_notes?: string;
  validation_flags: string[];
  revision_count: number;
  practical_tips: string[];
  days: ItineraryDay[];
}

export interface AgentRun {
  id: number;
  trip_id: number;
  agent_name: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  logs?: string;
  output_summary?: string;
}

export interface TripListItem {
  id: number;
  title: string;
  origin?: string;
  destination: string;
  start_date?: string;
  end_date?: string;
  duration_days: number;
  travellers: number;
  budget?: number;
  currency: string;
  travel_style?: string;
  status: "draft" | "planning" | "completed" | "failed";
  summary?: string;
  created_at: string;
}

export interface TripDetail extends TripListItem {
  user_id: number;
  interests: string[];
  dietary_preferences: string[];
  accommodation_preferences?: string;
  updated_at: string;
  flight_research?: FlightResearch;
  hotel_research?: HotelResearch;
  destination_research?: DestinationResearch;
  weather_research?: WeatherResearch;
  food_research?: FoodResearch;
  activity_research?: ActivityResearch;
  budget_details?: Budget;
  itinerary?: Itinerary;
  sources: ResearchSource[];
  agent_runs: AgentRun[];
}

export interface AgentStatusInfo {
  status: "pending" | "running" | "completed" | "failed";
  message: string;
}

export interface ProgressState {
  trip_id: number;
  current_stage: string;
  progress_percentage: number;
  status: "running" | "completed" | "failed";
  message: string;
  agents: Record<string, AgentStatusInfo>;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  sender: "user" | "assistant";
  content: string;
  actions_taken?: Record<string, any>;
  sources?: Array<{
    source_type: string;
    title: string;
    url?: string | null;
    source?: string;
    chunk_id?: number;
    snippet?: string;
  }>;
  created_at: string;
}

export interface Conversation {
  id: number;
  trip_id: number;
  messages: ChatMessage[];
  created_at: string;
}
