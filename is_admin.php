// checks all users to find wordpress admin priviledges
function is_administrator($user_id=0)
{
    $user = new WP_User( intval($user_id) );
    $admin = false;
    
    if ( !empty( $user->roles ) && is_array( $user->roles ) ) {
        foreach ( $user->roles as $role ) {
            if ( strtolower($role) == 'administrator') {
              $admin = true;
            }
        }
    }
    return $admin;
}
