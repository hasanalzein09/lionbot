import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import 'user_form_screen.dart';

class UsersScreen extends StatefulWidget {
  const UsersScreen({super.key});

  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends State<UsersScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _allUsers = [];
  bool _isLoading = true;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadUsers();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadUsers() async {
    setState(() => _isLoading = true);
    try {
      final users = await ApiService().getUsers();
      if (mounted) setState(() { _allUsers = users; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to load users'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  List<dynamic> _getFilteredUsers(String? role) {
    var filtered = _allUsers;
    
    // Filter by role
    if (role != null) {
      filtered = filtered.where((u) => u['role'] == role).toList();
    }
    
    // Filter by search
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((u) {
        final name = (u['full_name'] ?? '').toString().toLowerCase();
        final phone = (u['phone_number'] ?? '').toString().toLowerCase();
        final email = (u['email'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        return name.contains(query) || phone.contains(query) || email.contains(query);
      }).toList();
    }
    
    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Users Management'),
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppTheme.primaryColor,
          unselectedLabelColor: AppTheme.textMuted,
          indicatorColor: AppTheme.primaryColor,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Admins'),
            Tab(text: 'Restaurants'),
            Tab(text: 'Drivers'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadUsers,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              onChanged: (v) => setState(() => _searchQuery = v),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Search users...',
                prefixIcon: const Icon(Icons.search, color: AppTheme.textMuted),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, color: AppTheme.textMuted),
                        onPressed: () => setState(() => _searchQuery = ''),
                      )
                    : null,
              ),
            ),
          ),
          
          // Users list
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
                : TabBarView(
                    controller: _tabController,
                    children: [
                      _buildUsersList(null),
                      _buildUsersList('admin'),
                      _buildUsersList('restaurant_owner'),
                      _buildUsersList('driver'),
                    ],
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppTheme.primaryColor,
        onPressed: () => _navigateToForm(null),
        child: const Icon(Icons.add, color: Colors.black),
      ),
    );
  }

  Widget _buildUsersList(String? role) {
    final users = _getFilteredUsers(role);
    
    if (users.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_outline, size: 64, color: Colors.white.withOpacity(0.3)),
            const SizedBox(height: 16),
            Text(
              'No users found',
              style: TextStyle(color: Colors.white.withOpacity(0.5)),
            ),
          ],
        ),
      );
    }
    
    return RefreshIndicator(
      onRefresh: _loadUsers,
      color: AppTheme.primaryColor,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: users.length,
        itemBuilder: (context, index) => _buildUserCard(users[index]),
      ),
    );
  }

  Widget _buildUserCard(Map<String, dynamic> user) {
    final role = user['role'] as String? ?? 'user';
    final isActive = user['is_active'] as bool? ?? true;
    
    Color roleColor;
    IconData roleIcon;
    
    switch (role) {
      case 'super_admin':
      case 'admin':
        roleColor = AppTheme.errorColor;
        roleIcon = Icons.admin_panel_settings;
        break;
      case 'restaurant_owner':
        roleColor = AppTheme.primaryColor;
        roleIcon = Icons.restaurant;
        break;
      case 'driver':
        roleColor = AppTheme.accentColor;
        roleIcon = Icons.delivery_dining;
        break;
      default:
        roleColor = AppTheme.textMuted;
        roleIcon = Icons.person;
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: Stack(
          children: [
            CircleAvatar(
              radius: 24,
              backgroundColor: roleColor.withOpacity(0.1),
              child: Icon(roleIcon, color: roleColor),
            ),
            if (!isActive)
              Positioned(
                right: 0,
                top: 0,
                child: Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: AppTheme.errorColor,
                    shape: BoxShape.circle,
                    border: Border.all(color: AppTheme.cardDark, width: 2),
                  ),
                ),
              ),
          ],
        ),
        title: Text(
          user['full_name'] ?? 'Unknown',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              user['phone_number'] ?? user['email'] ?? '',
              style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 13),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: roleColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _formatRole(role),
                style: TextStyle(color: roleColor, fontSize: 11),
              ),
            ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert, color: AppTheme.textMuted),
          color: AppTheme.surfaceDark,
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'edit', child: Row(children: [
              Icon(Icons.edit, size: 18, color: AppTheme.primaryColor),
              SizedBox(width: 8),
              Text('Edit'),
            ])),
            PopupMenuItem(value: 'toggle', child: Row(children: [
              Icon(isActive ? Icons.block : Icons.check_circle, size: 18, 
                  color: isActive ? AppTheme.errorColor : AppTheme.accentColor),
              const SizedBox(width: 8),
              Text(isActive ? 'Deactivate' : 'Activate'),
            ])),
            const PopupMenuItem(value: 'delete', child: Row(children: [
              Icon(Icons.delete, size: 18, color: AppTheme.errorColor),
              SizedBox(width: 8),
              Text('Delete', style: TextStyle(color: AppTheme.errorColor)),
            ])),
          ],
          onSelected: (action) => _handleUserAction(user, action),
        ),
        onTap: () => _navigateToForm(user),
      ),
    );
  }

  String _formatRole(String role) {
    switch (role) {
      case 'super_admin': return 'Super Admin';
      case 'admin': return 'Admin';
      case 'restaurant_owner': return 'Restaurant Owner';
      case 'driver': return 'Driver';
      default: return 'User';
    }
  }

  void _handleUserAction(Map<String, dynamic> user, String action) async {
    final userId = user['id'] as int?;
    if (userId == null) return;

    switch (action) {
      case 'edit':
        _navigateToForm(user);
        break;
      case 'toggle':
        final isActive = user['is_active'] as bool? ?? true;
        try {
          await ApiService().updateUser(userId, {'is_active': !isActive});
          _loadUsers();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('User ${isActive ? "deactivated" : "activated"}'),
                backgroundColor: AppTheme.accentColor,
              ),
            );
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Action failed'), backgroundColor: AppTheme.errorColor),
            );
          }
        }
        break;
      case 'delete':
        _showDeleteConfirmation(user);
        break;
    }
  }

  void _showDeleteConfirmation(Map<String, dynamic> user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('Delete User'),
        content: Text('Are you sure you want to delete ${user['full_name']}? This cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              try {
                await ApiService().deleteUser(user['id']);
                _loadUsers();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('User deleted'), backgroundColor: AppTheme.accentColor),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Delete failed'), backgroundColor: AppTheme.errorColor),
                  );
                }
              }
            },
            child: const Text('Delete', style: TextStyle(color: AppTheme.errorColor)),
          ),
        ],
      ),
    );
  }

  void _navigateToForm(Map<String, dynamic>? user) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => UserFormScreen(user: user)),
    );
    if (result == true) {
      _loadUsers();
    }
  }
}
