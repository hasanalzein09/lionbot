import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/api_service.dart';

// Restaurant Model
class RestaurantModel {
  final int id;
  final String name;
  final String? description;
  final String? category;
  final double? rating;
  final bool isActive;
  final String? imageUrl;


  RestaurantModel({
    required this.id,
    required this.name,
    this.description,
    this.category,
    this.rating,
    required this.isActive,
    this.imageUrl,
  });

  factory RestaurantModel.fromJson(Map<String, dynamic> json) {
    return RestaurantModel(
      id: json['id'],
      name: json['name'] ?? '',
      description: json['description'],
      category: json['category'],
      rating: json['rating']?.toDouble(),
      isActive: json['is_active'] ?? true,
      imageUrl: json['image_url'],
    );
  }
}

// Restaurants State
class RestaurantsState {
  final List<RestaurantModel> restaurants;
  final List<RestaurantModel> favorites;
  final bool isLoading;
  final String? error;

  RestaurantsState({
    this.restaurants = const [],
    this.favorites = const [],
    this.isLoading = false,
    this.error,
  });

  RestaurantsState copyWith({
    List<RestaurantModel>? restaurants,
    List<RestaurantModel>? favorites,
    bool? isLoading,
    String? error,
  }) {
    return RestaurantsState(
      restaurants: restaurants ?? this.restaurants,
      favorites: favorites ?? this.favorites,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// Restaurants Notifier
class RestaurantsNotifier extends StateNotifier<RestaurantsState> {
  RestaurantsNotifier() : super(RestaurantsState());

  final _api = ApiService();

  Future<void> loadRestaurants({String? category}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.getRestaurants(category: category);
      final restaurants = (data)
          .map((e) => RestaurantModel.fromJson(e))
          .toList();
      state = state.copyWith(restaurants: restaurants, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadFavorites() async {
    try {
      final response = await _api.client.get('/favorites');
      final data = response.data as List;
      final favorites = data
          .map((e) => RestaurantModel.fromJson(e['restaurant']))
          .toList();
      state = state.copyWith(favorites: favorites);
    } catch (e) {
      // Ignore favorites error
    }
  }

  Future<void> toggleFavorite(int restaurantId) async {
    final isFavorite = state.favorites.any((r) => r.id == restaurantId);
    
    try {
      if (isFavorite) {
        await _api.client.delete('/favorites/$restaurantId');
        state = state.copyWith(
          favorites: state.favorites.where((r) => r.id != restaurantId).toList(),
        );
      } else {
        await _api.client.post('/favorites/$restaurantId');
        final restaurant = state.restaurants.firstWhere((r) => r.id == restaurantId);
        state = state.copyWith(
          favorites: [...state.favorites, restaurant],
        );
      }
    } catch (e) {
      // Revert on error
      await loadFavorites();
    }
  }

  bool isFavorite(int restaurantId) {
    return state.favorites.any((r) => r.id == restaurantId);
  }
}

// Provider
final restaurantsProvider = StateNotifierProvider<RestaurantsNotifier, RestaurantsState>((ref) {
  return RestaurantsNotifier();
});
