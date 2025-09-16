import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock the API
vi.mock('../../services/api', () => ({
  authAPI: {
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
  },
}))

// Test component to access auth context
const TestComponent = () => {
  const { user, isAuthenticated, login, logout, hasRole } = useAuth()
  
  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'authenticated' : 'not-authenticated'}
      </div>
      <div data-testid="user-info">
        {user ? `${user.username} - ${user.roles?.map(r => r.name).join(', ')}` : 'no-user'}
      </div>
      <button onClick={() => login('token', { id: 1, username: 'testuser', roles: [{ name: 'Staff Member' }] })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
      <div data-testid="has-staff-role">
        {hasRole('Staff Member') ? 'has-staff-role' : 'no-staff-role'}
      </div>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('provides initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated')
    expect(screen.getByTestId('user-info')).toHaveTextContent('no-user')
    expect(screen.getByTestId('has-staff-role')).toHaveTextContent('no-staff-role')
  })

  it('handles login correctly', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const loginButton = screen.getByText('Login')
    
    await act(async () => {
      loginButton.click()
    })
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated')
    expect(screen.getByTestId('user-info')).toHaveTextContent('testuser - Staff Member')
    expect(screen.getByTestId('has-staff-role')).toHaveTextContent('has-staff-role')
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'token')
  })

  it('handles logout correctly', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // First login
    const loginButton = screen.getByText('Login')
    await act(async () => {
      loginButton.click()
    })
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated')
    
    // Then logout
    const logoutButton = screen.getByText('Logout')
    await act(async () => {
      logoutButton.click()
    })
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated')
    expect(screen.getByTestId('user-info')).toHaveTextContent('no-user')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
  })

  it('checks roles correctly', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const loginButton = screen.getByText('Login')
    
    await act(async () => {
      loginButton.click()
    })
    
    expect(screen.getByTestId('has-staff-role')).toHaveTextContent('has-staff-role')
  })

  it('restores authentication from localStorage', async () => {
    const { authAPI } = await import('../../services/api')
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'stored-token'
      return null
    })
    
    authAPI.getCurrentUser.mockResolvedValue({
      data: {
        user: {
          id: 1,
          username: 'storeduser',
          roles: [{ name: 'HR Admin' }]
        }
      }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Wait for the effect to run
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0))
    })
    
    expect(authAPI.getCurrentUser).toHaveBeenCalled()
  })

  it('handles token refresh failure', async () => {
    const { authAPI } = await import('../../services/api')
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'expired-token'
      return null
    })
    
    authAPI.getCurrentUser.mockRejectedValue(new Error('Token expired'))
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Wait for the effect to run
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0))
    })
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
  })
})

